# Wu-Tang Lyrics Splitter: TDD Implementation Plan

This document outlines the step-by-step process to build the lyrics splitting software, guided by the test stubs in `tests/test_split_lyrics_by_performer.py`.

## 1. Import the Lyrics Text File
- [x] Implement logic to load and read the full contents of `wu-tang-clan-lyrics-dataset/wu-tang.txt`.
- [x] Handle file not found and encoding errors gracefully.
- [x] Test: `test_import_wu_tang_txt`

## 2. Trim and Extract Key Candidates
- [x] Parse the loaded text for `[xxx]` key patterns.
- [x] Trim whitespace and remove extraneous characters from key candidates.
- [x] Test: `test_trim_and_extract_key_candidates`

## 3. Identify Performer Keys
- [x] Load `src/performer_aliases.json` and build a mapping of canonical performer names and aliases.
- [x] Match key candidates against the alias mapping to identify performer keys.
- [X] Test: `test_identify_performer_keys`

## 4. Identify Non-Performer Keys
- [x] Define and detect "fake keys" (e.g., chorus, 2x, etc.) that do not indicate a performer.
- [x] Define and detect "ignore keys" (e.g., [all], [sample]) that signal the following section should be skipped.
- [x] Test: `test_identify_fake_and_ignore_keys`

## 5. Ignore Sections After Ignore Keys
- [x] Implement logic to skip all lines after an ignore key until the next valid performer key.
- [x] Test: `test_ignore_sections_after_ignore_keys`

## 6. Output Text Files for Performers
- [ ] For each canonical performer, output a text file containing their lyrics.
- [ ] Ensure only valid performer keys (from the alias mapping) are used for output.
- [ ] Test: `test_output_all_performer_files`

## 7. Output for a Specific Performer
- [ ] Allow user to specify a performer (by canonical name or alias) and output only that performer's lyrics.
- [ ] Test: `test_output_specific_performer`

## 8. Refactor and Polish
- [ ] Refactor code for clarity, maintainability, and efficiency.
- [ ] Add docstrings and comments.
- [ ] Ensure all tests pass and code is robust to edge cases.

---

**Development Process:**
- Implement each step in order, making the corresponding test pass before moving to the next.
- Use the test suite as a guide and safety net for refactoring.
- Expand tests as new edge cases or requirements are discovered.

**Goal:**
- Fully tested, robust, and maintainable code for splitting Wu-Tang lyrics by performer, ready for LLM training or analysis.
