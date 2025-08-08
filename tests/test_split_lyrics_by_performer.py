import os
import tempfile
import shutil
import unittest

from src.split_lyrics_by_performer import classify_key, IGNORE_SET

def make_test_file(lines):
    tmpdir = tempfile.mkdtemp()
    testfile = os.path.join(tmpdir, 'test.txt')
    with open(testfile, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    return testfile, tmpdir

# 1. Import the Lyrics Text File
class TestImportLyricsFile(unittest.TestCase):
    """
    Tests for importing and reading the lyrics text file, including error handling.
    """
    def test_load_lyrics_file(self):
        """Test loading and reading the full contents of the lyrics file."""
        from src.split_lyrics_by_performer import load_lyrics_file
        # Use the actual dataset file for this test
        lyrics_path = os.path.join(os.path.dirname(__file__), '../wu-tang-clan-lyrics-dataset/wu-tang.txt')
        lyrics_path = os.path.abspath(lyrics_path)
        contents = load_lyrics_file(lyrics_path)
        # Check that the file is not empty and contains expected performer label(s)
        self.assertIsInstance(contents, str)
        self.assertTrue(len(contents) > 100)  # Should be a large file
        self.assertIn('[raekwon]', contents.lower())

    def test_file_not_found(self):
        """Test handling of file not found error."""
        from src.split_lyrics_by_performer import load_lyrics_file
        missing_path = os.path.join(os.path.dirname(__file__), 'this_file_does_not_exist.txt')
        with self.assertRaises(FileNotFoundError):
            load_lyrics_file(missing_path)

    def test_encoding_error(self):
        """Test handling of encoding errors when reading file."""
        from src.split_lyrics_by_performer import load_lyrics_file
        # Create a file with invalid utf-8 bytes
        tmpdir = tempfile.mkdtemp()
        bad_file = os.path.join(tmpdir, 'bad_encoding.txt')
        # Write some bytes that are not valid UTF-8
        with open(bad_file, 'wb') as f:
            f.write(b'\xff\xfe\xfd\xfc')
        # Now try to read it as utf-8, should raise UnicodeDecodeError
        with self.assertRaises(UnicodeDecodeError):
            load_lyrics_file(bad_file)
        shutil.rmtree(tmpdir)

# 2. Trim and Extract Key Candidates
class TestTrimAndExtractKeyCandidates(unittest.TestCase):
    """
    Tests for extracting and cleaning [xxx] key patterns from lyrics lines.
    """
    def test_extract_key_patterns(self):
        """Test parsing for [xxx] key patterns and cleaning with trim/replace chars."""
        from src.split_lyrics_by_performer import extract_key_candidates_from_lines
        lines = [
            "[raekwon]",
            "[rza & gza]",
            "[ghostface/rza]",
            "[  meth  ]",
            "[u-god:]",
            "[inspectah deck / masta killa]",
            "[rza: the genius]",
            "[rza & gza / odb]",
            "[rza: & gza / odb]",
            "[ rza/gza:odb ]",
            "[mister rogers]"
        ]
        # Default: trim ':'; replace '&', '/'
        expected = [
            "raekwon",
            "rza gza",
            "ghostface rza",
            "meth",
            "u god",
            "inspectah deck masta killa",
            "rza the genius",
            "rza gza odb",
            "rza gza odb",
            "rza gza odb",
            "mister rogers"
        ]
        result = extract_key_candidates_from_lines(lines)
        # Normalize double spaces to single for comparison
        norm = lambda s: ' '.join(s.split())
        result = [norm(k) for k in result]
        expected = [norm(k) for k in expected]
        self.assertEqual(result, expected)

    def test_custom_trim_and_replace(self):
        """Test custom trim and replace chars in key extraction."""
        from src.split_lyrics_by_performer import extract_key_candidates_from_lines
        lines = ["[rza*odb]", "[ghostface+gza]"]
        # Trim '*', replace '+' with space
        expected = ["rza odb", "ghostface gza"]
        result = extract_key_candidates_from_lines(
            lines,
            trim_chars=['*'],
            replace_with_space_chars=['+']
        )
        norm = lambda s: ' '.join(s.split())
        result = [norm(k) for k in result]
        expected = [norm(k) for k in expected]
        self.assertEqual(result, expected)

# 3. Identify Performer Keys
class TestIdentifyPerformerKeys(unittest.TestCase):
    def test_multi_performer_key_maps_to_all_canonical(self):
        """Test that a key like 'odb rza' identifies both 'ol' dirty bastard' and 'rza' using the real alias mapping."""
        import json
        from src.split_lyrics_by_performer import match_key_to_canonical
        alias_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/performer_aliases.json'))
        with open(alias_path, 'r', encoding='utf-8') as f:
            alias_map = json.load(f)
        # Split the key and map each part
        key = 'odb rza'
        parts = key.split()
        mapped = set()
        for part in parts:
            canonical = match_key_to_canonical(part, alias_map)
            if canonical:
                mapped.add(canonical)
        self.assertIn("ol' dirty bastard", mapped)
        self.assertIn("rza", mapped)
    def test_real_alias_mapping(self):
        """Test that the real performer_aliases.json maps representative aliases to canonical names."""
        import json
        from src.split_lyrics_by_performer import match_key_to_canonical
        alias_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/performer_aliases.json'))
        with open(alias_path, 'r', encoding='utf-8') as f:
            alias_map = json.load(f)
        # Pick a few canonical performers and representative aliases to test
        test_cases = [
            ("rza", ["rza", "bobby digital", "the abbot"]),
            ("gza", ["gza", "the genius"]),
            ("method man", ["method man", "meth", "johnny blaze"]),
            ("ghostface killah", ["ghostface killah", "ghostface", "tony starks"]),
            ("inspectah deck", ["inspectah deck", "deck"]),
            ("ol' dirty bastard", ["ol' dirty bastard", "odb", "dirt mcgirt"]),
            ("masta killa", ["masta killa", "noodles"]),
            ("u-god", ["u-god", "golden arms"]),
            ("cappadonna", ["cappadonna", "cappa"]),
        ]
        for canonical, aliases in test_cases:
            for alias in aliases:
                result = match_key_to_canonical(alias, alias_map)
                self.assertEqual(result, canonical, f"Alias '{alias}' should map to '{canonical}'")
    """
    Tests for loading performer alias mappings and matching keys to canonical performer names.
    """
    def test_load_alias_mapping(self):
        """Test loading performer aliases mapping from JSON."""
        import json
        import tempfile
        # Create a fake alias mapping JSON file
        alias_map = {
            "rza": ["rza", "bobby digital", "the abbot"],
            "gza": ["gza", "the genius"],
            "method man": ["method man", "meth", "johnny blaze"]
        }
        tmpdir = tempfile.mkdtemp()
        alias_path = os.path.join(tmpdir, "aliases.json")
        with open(alias_path, 'w', encoding='utf-8') as f:
            json.dump(alias_map, f)
        # Load and check
        with open(alias_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, alias_map)
        shutil.rmtree(tmpdir)

    def test_match_key_to_alias(self):
        """Test matching key candidates to performer aliases."""
        from src.split_lyrics_by_performer import match_key_to_canonical
        alias_map = {
            "rza": ["rza", "bobby digital", "the abbot"],
            "gza": ["gza", "the genius"],
            "method man": ["method man", "meth", "johnny blaze"]
        }
        # Should match canonical name
        self.assertEqual(match_key_to_canonical("rza", alias_map), "rza")
        self.assertEqual(match_key_to_canonical("bobby digital", alias_map), "rza")
        self.assertEqual(match_key_to_canonical("the abbot", alias_map), "rza")
        self.assertEqual(match_key_to_canonical("gza", alias_map), "gza")
        self.assertEqual(match_key_to_canonical("the genius", alias_map), "gza")
        self.assertEqual(match_key_to_canonical("meth", alias_map), "method man")
        self.assertEqual(match_key_to_canonical("johnny blaze", alias_map), "method man")
        # Should return None for unknown
        self.assertIsNone(match_key_to_canonical("ghostface", alias_map))


# 4. Classify Keys
class TestClassifyKeys(unittest.TestCase):
    """
    Tests for classifying keys as performer, ignore, or skip, using static sets and the full labeled file.
    """

    @classmethod
    def setUpClass(cls):
        import json
        alias_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/performer_aliases.json'))
        with open(alias_path, 'r', encoding='utf-8') as f:
            cls.alias_map = json.load(f)
        # Use IGNORE_SET from src.split_lyrics_by_performer
        cls.ignore_set = IGNORE_SET
        # Load labeled keys
        labeled_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/unique_keys_labeled.json'))
        with open(labeled_path, 'r', encoding='utf-8') as f:
            cls.labeled_keys = json.load(f)

    def test_static_classification(self):
        """Test static examples for each class."""
        self.assertEqual(classify_key("rza", self.alias_map, self.ignore_set), "performer")
        self.assertEqual(classify_key("chorus rza", self.alias_map, self.ignore_set), "performer")
        self.assertEqual(classify_key("chorus", self.alias_map, self.ignore_set), "ignore")
        self.assertEqual(classify_key("all", self.alias_map, self.ignore_set), "skip")
        self.assertEqual(classify_key("sample", self.alias_map, self.ignore_set), "skip")
        self.assertEqual(classify_key("chorus 2x", self.alias_map, self.ignore_set), "ignore")
        self.assertEqual(classify_key("ghostface killah", self.alias_map, self.ignore_set), "performer")
        self.assertEqual(classify_key("chorus ghostface killah", self.alias_map, self.ignore_set), "performer")
        self.assertEqual(classify_key("random label", self.alias_map, self.ignore_set), "skip")

    def test_labeled_file_classification(self):
        """Test that all keys in unique_keys_labeled.json are classified as expected (ignoring 'unknown')."""
        mismatches = []
        for entry in self.labeled_keys:
            key = entry.get("key")
            expected = entry.get("type")
            if expected == "unknown" or key is None:
                continue
            actual = classify_key(key, self.alias_map, self.ignore_set)
            if actual != expected:
                mismatches.append((key, expected, actual))
        if mismatches:
            print("\nMismatches between labeled file and classifier:")
            for key, expected, actual in mismatches:
                print(f"  key: {key!r:30} expected: {expected!r:10} actual: {actual!r}")
            print(f"Total mismatches: {len(mismatches)}")
        self.assertTrue(len(mismatches) == 0, f"There are {len(mismatches)} mismatches between labeled file and classifier.")


# 5. Ignore Sections After Ignore Keys
class TestIgnoreSectionsAfterIgnoreKeys(unittest.TestCase):
    """
    Tests for skipping sections of lyrics after ignore keys until the next valid performer key.
    """
    def test_skip_lines_after_ignore_key(self):
        """
        Test that lines after an ignore key are skipped until the next performer key.
        """
        from src.split_lyrics_by_performer import classify_key, IGNORE_SET
        # You will implement split_lyrics_by_performer in the main module
        from src.split_lyrics_by_performer import split_lyrics_by_performer

        # Simulated lyrics
        lines = [
            "[rza]",
            "RZA verse 1",
            "RZA verse 2",
            "[chorus]",
            "Chorus line 1",
            "Chorus line 2",
            "[gza]",
            "GZA verse 1",
            "[skit]",
            "Skit line 1",
            "[method man]",
            "Meth verse 1",
            "Meth verse 2"
        ]
        # Simulated alias map
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"],
            "method man": ["method man", "meth"]
        }

        # Run the splitter
        performer_chunks = split_lyrics_by_performer(lines, alias_map, IGNORE_SET)

        # Expected output:
        # - RZA: ["RZA verse 1", "RZA verse 2"]
        # - GZA: ["GZA verse 1"]
        # - Method Man: ["Meth verse 1", "Meth verse 2"]
        # - Chorus and Skit lines should be ignored

        self.assertEqual(performer_chunks["rza"], ["RZA verse 1", "RZA verse 2"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse 1"])
        self.assertEqual(performer_chunks["method man"], ["Meth verse 1", "Meth verse 2"])
        # Optionally, check that ignored sections are not present
        for performer in performer_chunks:
            for line in performer_chunks[performer]:
                self.assertNotIn("Chorus", line)
                self.assertNotIn("Skit", line)
    
    def test_multi_performer_key_triggers_skip(self):
        """
        Test that a key mentioning multiple performers triggers a skip (no attribution).
        """
        from src.split_lyrics_by_performer import split_lyrics_by_performer, IGNORE_SET
    
        lines = [
            "[rza]",
            "RZA verse",
            "[rza gza]",
            "Collab verse",
            "[gza]",
            "GZA verse"
        ]
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"]
        }
        performer_chunks = split_lyrics_by_performer(lines, alias_map, IGNORE_SET)
        self.assertEqual(performer_chunks["rza"], ["RZA verse"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse"])
        # "Collab verse" should not be attributed to anyone
        for performer in performer_chunks:
            self.assertNotIn("Collab verse", performer_chunks[performer])

    def test_multiple_ignore_keys(self):
        """
        Test that multiple ignore keys in sequence skip all lines until next performer key.
        """
        from src.split_lyrics_by_performer import split_lyrics_by_performer, IGNORE_SET
    
        lines = [
            "[rza]",
            "RZA verse",
            "[chorus]",
            "Chorus line",
            "[skit]",
            "Skit line",
            "[gza]",
            "GZA verse"
        ]
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"]
        }
        performer_chunks = split_lyrics_by_performer(lines, alias_map, IGNORE_SET)
        self.assertEqual(performer_chunks["rza"], ["RZA verse"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse"])


    def test_skip_key_does_not_attribute(self):
        """
        Test that lines after a skip key are not attributed to any performer.
        """
        from src.split_lyrics_by_performer import split_lyrics_by_performer, IGNORE_SET
    
        lines = [
            "[rza]",
            "RZA verse",
            "[all]",
            "Group line",
            "[gza]",
            "GZA verse"
        ]
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"]
        }
        performer_chunks = split_lyrics_by_performer(lines, alias_map, IGNORE_SET)
        self.assertEqual(performer_chunks["rza"], ["RZA verse"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse"])
        # "Group line" should not be attributed
        for performer in performer_chunks:
            self.assertNotIn("Group line", performer_chunks[performer])

# 6. Output Text Files for Performers
class TestOutputTextFilesForPerformers(unittest.TestCase):
    """
    Tests for outputting text files for all canonical performers and ensuring only valid keys are used.
    """
    def test_output_files_for_all_performers(self):
        """
        Test that output files are created for all canonical performers and contain correct lyrics.
        """
        import tempfile
        import os
        import shutil
        from src.split_lyrics_by_performer import write_performer_files
    
        # Simulated performer chunks
        performer_chunks = {
            "rza": ["RZA verse 1", "RZA verse 2"],
            "gza": ["GZA verse 1"],
            "method man": []
        }
        # Create a temporary output directory
        out_dir = tempfile.mkdtemp()
        try:
            write_performer_files(performer_chunks, out_dir)
            # Check that files exist and contents are correct
            for performer, lines in performer_chunks.items():
                out_path = os.path.join(out_dir, f"{performer.replace(' ', '_')}.txt")
                self.assertTrue(os.path.exists(out_path), f"File for {performer} not found")
                with open(out_path, "r", encoding="utf-8") as f:
                    contents = f.read().splitlines()
                self.assertEqual(contents, lines)
        finally:
            shutil.rmtree(out_dir)
    
    def test_only_valid_performer_keys_used(self):
        """
        Test that only valid performer keys are used for output (no extra files).
        """
        import tempfile
        import os
        import shutil
        from src.split_lyrics_by_performer import write_performer_files

        performer_chunks = {
            "rza": ["RZA verse"],
            "gza": ["GZA verse"],
            "not_a_performer": ["Should not be written"]
        }
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"]
        }
        out_dir = tempfile.mkdtemp()
        try:
            write_performer_files(performer_chunks, out_dir, alias_map=alias_map)
            expected_files = {"rza.txt", "gza.txt"}
            actual_files = set(os.listdir(out_dir))
            self.assertTrue(expected_files.issubset(actual_files))
            self.assertNotIn("not_a_performer.txt", actual_files)
        finally:
            shutil.rmtree(out_dir)

# 7. Output for a Specific Performer
class TestOutputForSpecificPerformer(unittest.TestCase):
    """
    Tests for outputting text files for a specific performer or alias.
    """
    def test_output_for_specified_performer(self):
        """Test output for a specified performer (canonical or alias)."""
        self.skipTest("Not implemented: output for specified performer")

# 8. Refactor and Polish
class TestRefactorAndPolish(unittest.TestCase):
    """
    Meta-tests for code clarity, maintainability, and integration.
    """
    def test_code_clarity_and_comments(self):
        """Test code is clear, maintainable, and well-commented."""
        self.skipTest("Not implemented: code clarity and comments")

    def test_all_tests_pass(self):
        """Test that all other tests pass (integration check)."""
        self.skipTest("Not implemented: all tests pass integration")


if __name__ == '__main__':
    unittest.main()
