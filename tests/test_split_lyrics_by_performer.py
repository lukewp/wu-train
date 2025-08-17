import os
import tempfile
import shutil
import unittest
import json

from io import StringIO
from contextlib import contextmanager

import pycodestyle

from src.split_lyrics_by_performer import *


# Context manager for temporary directories
@contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)


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
    Tests for importing and reading the lyrics text file, including error
    handling.
    """
    def test_load_lyrics_file(self):
        """
        Test loading and reading the full contents of a lyrics file
            (temp file, does not overwrite real dataset).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            lyrics_path = os.path.join(tmpdir, 'test_lyrics.txt')
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                f.write("[raekwon]\n" + ("sample lyric line " * 8))
            contents = load_lyrics_file(lyrics_path)
            # Check that the file is not empty and contains expected label(s)
            self.assertIsInstance(contents, str)
            self.assertTrue(len(contents) > 100)
            self.assertIn('[raekwon]', contents.lower())

    def test_file_not_found(self):
        """Test handling of file not found error."""
        missing_path = os.path.join(
            os.path.dirname(__file__),
            'this_file_does_not_exist.txt'
        )
        with self.assertRaises(FileNotFoundError):
            load_lyrics_file(missing_path)

    def test_encoding_error(self):
        """Test handling of encoding errors when reading file."""
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
        """
        Test parsing for [xxx] key patterns and cleaning with
          trim/replace chars.
        """
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

        def norm(s):
            return ' '.join(s.split())
        result = [norm(k) for k in result]
        expected = [norm(k) for k in expected]
        self.assertEqual(result, expected)

    def test_custom_trim_and_replace(self):
        """Test custom trim and replace chars in key extraction."""
        lines = ["[rza*odb]", "[ghostface+gza]"]
        # Trim '*', replace '+' with space
        expected = ["rza odb", "ghostface gza"]
        result = extract_key_candidates_from_lines(
            lines,
            trim_chars=['*'],
            replace_with_space_chars=['+']
        )

        def norm(s):
            return ' '.join(s.split())
        result = [norm(k) for k in result]
        expected = [norm(k) for k in expected]
        self.assertEqual(result, expected)


# 3. Identify Performer Keys
class TestIdentifyPerformerKeys(unittest.TestCase):
    def test_multi_performer_key_maps_to_all_canonical(self):
        """
        Test that a key like 'odb rza' identifies both 'ol' dirty bastard'
          and 'rza' using the real alias mapping.
        """
        alias_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../src/performer_aliases.json'
            )
        )
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
        """
        Test that the real performer_aliases.json maps representative
        aliases to canonical names.
        """
        alias_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../src/performer_aliases.json'
            )
        )
        with open(alias_path, 'r', encoding='utf-8') as f:
            alias_map = json.load(f)
        # Pick a few canonical performers and representative aliases to test
        test_cases = [
            ("rza", ["rza", "bobby digital", "the abbot"]),
            ("gza", ["gza", "the genius"]),
            ("method man", ["method man", "meth", "johnny blaze"]),
            ("ghostface killah", ["ghostface killah", "ghostface",
                                  "tony starks"]),
            ("inspectah deck", ["inspectah deck", "deck"]),
            ("ol' dirty bastard", ["ol' dirty bastard", "odb",
                                   "dirt mcgirt"]),
            ("masta killa", ["masta killa", "noodles"]),
            ("u-god", ["u-god", "golden arms"]),
            ("cappadonna", ["cappadonna", "cappa"]),
        ]
        for canonical, aliases in test_cases:
            for alias in aliases:
                result = match_key_to_canonical(alias, alias_map)
                self.assertEqual(result,
                                 canonical,
                                 f"Alias '{alias}' should map to '{canonical}'"
                                 )
    """
    Tests for loading performer alias mappings and matching keys to canonical
    performer names.
    """
    def test_load_alias_mapping(self):
        """Test loading performer aliases mapping from JSON."""
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
        alias_map = {
            "rza": ["rza", "bobby digital", "the abbot"],
            "gza": ["gza", "the genius"],
            "method man": ["method man", "meth", "johnny blaze"]
        }
        # Should match canonical name
        self.assertEqual(
            match_key_to_canonical("rza", alias_map), "rza"
        )
        self.assertEqual(
            match_key_to_canonical("bobby digital", alias_map), "rza"
        )
        self.assertEqual(
            match_key_to_canonical("the abbot", alias_map), "rza"
        )
        self.assertEqual(
            match_key_to_canonical("gza", alias_map), "gza"
        )
        self.assertEqual(
            match_key_to_canonical("the genius", alias_map), "gza"
        )
        self.assertEqual(
            match_key_to_canonical("meth", alias_map), "method man"
        )
        self.assertEqual(
            match_key_to_canonical("johnny blaze", alias_map), "method man"
        )
        # Should return None for unknown
        self.assertIsNone(
            match_key_to_canonical("ghostface", alias_map)
        )


# 4. Classify Keys
class TestClassifyKeys(unittest.TestCase):
    """
    Tests for classifying keys as performer, ignore, or skip, using static
      sets and the full labeled file.
    """

    @classmethod
    def setUpClass(cls):
        alias_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../src/performer_aliases.json'
            )
        )
        with open(alias_path, 'r', encoding='utf-8') as f:
            cls.alias_map = json.load(f)
        # Use IGNORE_SET from src.split_lyrics_by_performer
        cls.ignore_set = IGNORE_SET
        # Load labeled keys
        labeled_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../tests/unique_keys_labeled.json'
            )
        )
        with open(labeled_path, 'r', encoding='utf-8') as f:
            cls.labeled_keys = json.load(f)

    def test_static_classification(self):
        """Test static examples for each class."""
        self.assertEqual(
            classify_key("rza", self.alias_map, self.ignore_set),
            "performer"
        )
        self.assertEqual(
            classify_key("chorus rza", self.alias_map, self.ignore_set),
            "performer"
        )
        self.assertEqual(
            classify_key("chorus", self.alias_map, self.ignore_set),
            "ignore"
        )
        self.assertEqual(
            classify_key("all", self.alias_map, self.ignore_set),
            "skip"
        )
        self.assertEqual(
            classify_key("sample", self.alias_map, self.ignore_set),
            "skip"
        )
        self.assertEqual(
            classify_key("chorus 2x", self.alias_map, self.ignore_set),
            "ignore"
        )
        self.assertEqual(
            classify_key("ghostface killah", self.alias_map, self.ignore_set),
            "performer"
        )
        self.assertEqual(
            classify_key("chorus ghostface killah",
                         self.alias_map, self.ignore_set),
            "performer"
        )
        self.assertEqual(
            classify_key("random label", self.alias_map, self.ignore_set),
            "skip"
        )

    def test_labeled_file_classification(self):
        """
        Test that all keys in unique_keys_labeled.json are classified as
          expected (ignoring 'unknown').
        """
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
                print(
                    f"  key: {key!r:30} "
                    f"expected: {expected!r:10} "
                    f"actual: {actual!r}"
                )
            print(f"Total mismatches: {len(mismatches)}")
        self.assertTrue(
            len(mismatches) == 0,
            f"{len(mismatches)} mismatches between labeled file and "
            "classifier."
        )


# 5. Ignore Sections After Ignore Keys
class TestIgnoreSectionsAfterIgnoreKeys(unittest.TestCase):
    """
    Tests for skipping sections of lyrics after ignore keys until the next
      valid performer key.
    """
    def test_skip_lines_after_ignore_key(self):
        """
        Test that lines after an ignore key are skipped until the next
          performer key.
        """
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
        performer_chunks = split_lyrics_by_performer(lines,
                                                     alias_map,
                                                     IGNORE_SET
                                                     )

        # Expected output:
        # - RZA: ["RZA verse 1", "RZA verse 2"]
        # - GZA: ["GZA verse 1"]
        # - Method Man: ["Meth verse 1", "Meth verse 2"]
        # - Chorus and Skit lines should be ignored
        self.assertEqual(
            performer_chunks["rza"],
            ["RZA verse 1", "RZA verse 2"]
        )
        self.assertEqual(
            performer_chunks["gza"],
            ["GZA verse 1"]
        )
        self.assertEqual(
            performer_chunks["method man"],
            ["Meth verse 1", "Meth verse 2"]
        )
        # Optionally, check that ignored sections are not present
        for performer in performer_chunks:
            for line in performer_chunks[performer]:
                self.assertNotIn("Chorus", line)
                self.assertNotIn("Skit", line)

    def test_multi_performer_key_triggers_skip(self):
        """
        Test that a key mentioning multiple performers triggers a skip
        (no attribution).
        """
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
        performer_chunks = split_lyrics_by_performer(
            lines, alias_map, IGNORE_SET
        )
        self.assertEqual(
            performer_chunks["rza"], ["RZA verse"]
        )
        self.assertEqual(
            performer_chunks["gza"], ["GZA verse"]
        )
        # "Collab verse" should not be attributed to anyone
        for performer in performer_chunks:
            self.assertNotIn(
                             "Collab verse",
                             performer_chunks[performer]
                            )

    def test_multiple_ignore_keys(self):
        """
        Test that multiple ignore keys in sequence skip all lines until
          next performer key.
        """
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
        performer_chunks = split_lyrics_by_performer(
            lines, alias_map, IGNORE_SET
        )
        self.assertEqual(
            performer_chunks["rza"], ["RZA verse"]
        )
        self.assertEqual(
            performer_chunks["gza"], ["GZA verse"]
        )

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
        performer_chunks = split_lyrics_by_performer(
            lines, alias_map, IGNORE_SET
        )
        self.assertEqual(performer_chunks["rza"], ["RZA verse"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse"])

    def test_skip_key_does_not_attribute(self):
        """
        Test that lines after a skip key are not attributed to any performer.
        """
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
        performer_chunks = split_lyrics_by_performer(
            lines, alias_map, IGNORE_SET
        )
        self.assertEqual(performer_chunks["rza"], ["RZA verse"])
        self.assertEqual(performer_chunks["gza"], ["GZA verse"])
        # "Group line" should not be attributed
        for performer in performer_chunks:
            self.assertNotIn("Group line", performer_chunks[performer])


# 6. Output Text Files for Performers
class TestOutputTextFilesForPerformers(unittest.TestCase):
    """
    Tests for outputting text files for all canonical performers and
    ensuring only valid keys are used.
    """
    def test_output_files_for_all_performers(self):
        """
        Test that output files are created for all canonical performers
        and contain correct lyrics.
        """
        performer_chunks = {
            "rza": ["RZA verse 1", "RZA verse 2"],
            "gza": ["GZA verse 1"],
            "method man": []
        }
        with tempdir() as out_dir:
            write_performer_files(performer_chunks, out_dir)
            for performer, lines in performer_chunks.items():
                out_path = os.path.join(
                    out_dir,
                    f"{performer.replace(' ', '_')}.txt"
                )
                self.assertTrue(os.path.exists(out_path),
                                f"File for {performer} not found")
                with open(out_path, "r", encoding="utf-8") as f:
                    contents = f.read().splitlines()
                self.assertEqual(contents, lines)

    def test_only_valid_performer_keys_used(self):
        """
        Test that only valid performer keys are used for output
          (no extra files).
        """
        performer_chunks = {
            "rza": ["RZA verse"],
            "gza": ["GZA verse"],
            "not_a_performer": ["Should not be written"]
        }
        alias_map = {
            "rza": ["rza"],
            "gza": ["gza"]
        }
        with tempdir() as out_dir:
            write_performer_files(performer_chunks,
                                  out_dir,
                                  alias_map=alias_map)
            expected_files = {"rza.txt", "gza.txt"}
            actual_files = set(os.listdir(out_dir))
            self.assertTrue(expected_files.issubset(actual_files))
            self.assertNotIn("not_a_performer.txt", actual_files)


class TestJsonlPromptCompletionPairs(unittest.TestCase):
    """
    Tests for JSONL prompt/completion splitting logic based on verse breaks.
    """
    def setUp(self):
        # Example Inspectah Deck lyrics as in the user prompt
        self.deck_lyrics = [
            "ladies and gentlemen, we'd like to welcome to you",
            "all the way from the slums of shaolin",
            "special uninvited guests",
            "came in through the back door",
            "ladies and gentlemen, it's them!",
            "",
            "dance with the mantis, note the slim chances",
            "chant this, anthem swing like pete sampras",
            "takin it straight to big man on campus",
            "brandish your weapon or get dropped to the canvas",
            "scandalous, made the metro panic"
        ]

    def test_jsonl_pairs_respect_verse_breaks(self):
        """
        Test that JSONL chat-format pairs are split at verse breaks
         (empty lines).
        """
        performer = "inspectah deck"
        pairs = split_lines_to_jsonl_pairs(self.deck_lyrics, performer)

        expected = [
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "ladies and gentlemen, we'd like to welcome to you"
                        ),
                    },
                    {
                        "role": "assistant",
                        "content": "all the way from the slums of shaolin",
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "all the way from the slums of shaolin",
                    },
                    {
                        "role": "assistant",
                        "content": "special uninvited guests",
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "special uninvited guests",
                    },
                    {
                        "role": "assistant",
                        "content": "came in through the back door",
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "came in through the back door"
                    },
                    {
                        "role": "assistant",
                        "content": "ladies and gentlemen, it's them!"
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "dance with the mantis, note the slim "
                        "chances"
                    },
                    {
                        "role": "assistant",
                        "content": "chant this, anthem swing like pete sampras"
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "chant this, anthem swing like pete sampras"
                    },
                    {
                        "role": "assistant",
                        "content": "takin it straight to big man on campus"
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "takin it straight to big man on campus"
                    },
                    {
                        "role": "assistant",
                        "content": (
                            "brandish your weapon or get dropped to the canvas"
                        ),
                    },
                ]
            },
            {
                "conversations": [
                    {
                        "role": "system",
                        "content": (
                            "You are Wu-Tang Clan member inspectah deck. "
                            "When a user prompts you with one of your lyrics, "
                            "you deliver the next line."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "brandish your weapon or get dropped to the canvas"
                        ),
                    },
                    {
                        "role": "assistant",
                        "content": "scandalous, made the metro panic",
                    },
                ]
            },
        ]

        self.assertEqual(pairs, expected)


# 7. Output for a Specific Performer
class TestOutputForSpecificPerformer(unittest.TestCase):
    """
    Tests for outputting text files for a specific performer or alias.
    """
    def setUp(self):
        # Minimal alias map and performer_chunks for testing
        self.alias_map = {
            "rza": ["rza", "bobby digital"],
            "gza": ["gza", "the genius"],
            "method man": ["method man", "meth"]
        }
        self.performer_chunks = {
            "rza": ["RZA verse 1", "RZA verse 2"],
            "gza": ["GZA verse 1"],
            "method man": []
        }

    def test_output_for_canonical_performer(self):
        """Test output for a canonical performer name."""
        with tempdir() as out_dir:
            write_performer_files({"rza": self.performer_chunks["rza"]},
                                  out_dir,
                                  alias_map=self.alias_map)
            out_path = os.path.join(out_dir, "rza.txt")
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                contents = f.read().splitlines()
            self.assertEqual(contents, self.performer_chunks["rza"])
            self.assertEqual(set(os.listdir(out_dir)), {"rza.txt"})

    def test_output_for_alias(self):
        """Test output for a performer specified by alias."""
        with tempdir() as out_dir:
            canonical = match_key_to_canonical("bobby digital", self.alias_map)
            if canonical is None:
                self.fail("Canonical performer not found for 'bobby digital'")
            self.assertEqual(canonical, "rza")
            write_performer_files(
                {canonical: self.performer_chunks[canonical]},
                out_dir,
                alias_map=self.alias_map
            )
            out_path = os.path.join(out_dir, "rza.txt")
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                contents = f.read().splitlines()
            self.assertEqual(contents, self.performer_chunks["rza"])

    def test_unknown_performer_raises(self):
        """
        Test that specifying an unknown performer raises an error
            or does not write a file.
        """
        with tempdir() as out_dir:
            write_performer_files({"ghostface": ["Ghost verse"]},
                                  out_dir,
                                  alias_map=self.alias_map
                                  )
            self.assertNotIn("ghostface.txt", os.listdir(out_dir))

    def test_empty_output(self):
        """
        Test that a performer with no lyrics creates an empty file or as
          per design.
        """
        with tempdir() as out_dir:
            write_performer_files({"method man": []},
                                  out_dir,
                                  alias_map=self.alias_map
                                  )
            out_path = os.path.join(out_dir, "method_man.txt")
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                contents = f.read().splitlines()
            self.assertEqual(contents, [])

    def test_case_insensitivity(self):
        """Test that performer/alias lookup is case-insensitive."""
        with tempdir() as out_dir:
            canonical = match_key_to_canonical("RZA", self.alias_map)
            if canonical is None:
                self.fail("Canonical performer not found for 'RZA'")
            self.assertEqual(canonical, "rza")
            canonical2 = match_key_to_canonical("BoBbY DiGiTaL",
                                                self.alias_map
                                                )
            if canonical2 is None:
                self.fail("Canonical performer not found for 'BoBbY DiGiTaL'")
            self.assertEqual(canonical2, "rza")
            # Only use canonical as a key after None check
            performer_lines = self.performer_chunks[canonical]
            write_performer_files(
                {canonical: performer_lines},
                out_dir,
                alias_map=self.alias_map
            )
            self.assertTrue(
                os.path.exists(os.path.join(out_dir, "rza.txt"))
            )

    def test_output_directory_created(self):
        """Test that a non-existent output directory is created."""
        with tempdir() as tmpdir:
            out_dir = os.path.join(tmpdir, "new_out_dir")
            self.assertFalse(os.path.exists(out_dir))
            write_performer_files(
                {"rza": self.performer_chunks["rza"]},
                out_dir,
                alias_map=self.alias_map
            )
            self.assertTrue(os.path.exists(out_dir))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "rza.txt")))


# 8. Refactor and Polish
class TestRefactorAndPolish(unittest.TestCase):
    def test_pep8_compliance_test_module(self):
        """
        Test that test_split_lyrics_by_performer.py is PEP-8 compliant
          (pycodestyle).
        """
        file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'test_split_lyrics_by_performer.py'
            )
        )
        output = StringIO()
        style = pycodestyle.StyleGuide(quiet=False, stdout=output)
        result = style.check_files([file_path])
        violations = output.getvalue()
        if result.total_errors > 0:
            print(
                "\nPEP-8 violations in test_split_lyrics_by_performer.py:\n"
                + violations
            )
        self.assertEqual(
            result.total_errors, 0,
            f"PEP-8 violations found: {result.total_errors}\n{violations}"
        )
    """
    Meta-tests for code clarity, maintainability, and integration.
    """
    def test_pep8_compliance(self):
        """
        Test that split_lyrics_by_performer.py is PEP-8 compliant
          (pycodestyle).
        """
        file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../src/split_lyrics_by_performer.py'
            )
        )
        # Capture output
        output = StringIO()
        style = pycodestyle.StyleGuide(quiet=False, stdout=output)
        result = style.check_files([file_path])
        violations = output.getvalue()
        if result.total_errors > 0:
            print(
                "\nPEP-8 violations in split_lyrics_by_performer.py:\n"
                + violations
            )
        self.assertEqual(
            result.total_errors, 0,
            f"PEP-8 violations found: {result.total_errors}\n{violations}"
        )

    def test_all_tests_pass(self):
        """
        Integration test: Run all other tests in this module and assert
         that they pass. This ensures the test suite is passing as a whole.
        """
        # Discover all tests in this module except this one
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(__import__(__name__))

        # Flatten the suite to get all test cases
        def flatten_suite(suite):
            for item in suite:
                if isinstance(item, unittest.TestSuite):
                    yield from flatten_suite(item)
                else:
                    yield item
        tests = [t for t in flatten_suite(suite)
                 if getattr(t,
                            '_testMethodName',
                            None
                            ) != 'test_all_tests_pass']
        result = unittest.TestResult()
        for test in tests:
            test(result)
        # If there are any failures or errors, fail this test
        if result.failures or result.errors:
            msgs = []
            for test_case, msg in result.failures + result.errors:
                msgs.append(f"{test_case.id()}: {msg}")
            self.fail(f"Integration test failed:\n" + '\n'.join(msgs))


if __name__ == '__main__':
    unittest.main()
