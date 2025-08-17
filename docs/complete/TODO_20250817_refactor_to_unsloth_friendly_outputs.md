# TODO: Refactor to Unsloth-Friendly Outputs (ChatML Default)

Date: 2025-08-17

This document outlines the steps required to refactor the repository to support Unsloth-compatible output formats for LLM fine-tuning, with ChatML as the default. The overhaul will include CLI changes, output logic, unit tests, and documentation updates.

---

## 1. Output Format Refactor
- [x] Implement ChatML format as the default output for all JSONL exports:
    - Each line should be a JSON object: `{ "conversations": [ {"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...} ] }`
- [x] Add support for ShareGPT format via CLI flag (e.g., `--sharegpt`):
    - Each line: `{ "conversations": [ {"from": "system", ...}, {"from": "human", ...}, {"from": "gpt", ...} ] }`
- [x] Refactor output logic to cleanly support both formats (modular helpers).
- [x] Ensure all output files are compatible with Unsloth's chat_template reformatter (no post-processing required).

## 2. CLI & API Changes
- [x] Update CLI help and usage to document new flags (`--chatml`, `--sharegpt`).
- [x] Default to ChatML if no format is specified.
- [x] Allow user to select format for specific performer or all performers.

## 3. Unit Test Overhaul
- [x] Update all unit tests to validate new output formats:
    - Test ChatML output structure and content.
    - Test ShareGPT output structure and content.
    - Ensure tests cover edge cases (verse breaks, empty lines, aliases, ignore logic).
- [x] Add tests for CLI flag parsing and output selection.
- [x] Validate that concatenated output files remain valid for Unsloth ingestion.

## 4. Documentation Updates
- [x] Update README.md:
    - Document new output formats and CLI flags.
    - Provide format examples for ChatML and ShareGPT.
    - Add instructions for concatenating files and using with Unsloth.
- [x] Add section on compatibility with Unsloth and chat_template reformatter.
- [x] Update usage examples and output samples.

## 5. Interactive Notebook
- [x] Update interactive_lyrics_lookup.ipynb to support previewing both output formats.
- [x] Add cells to demonstrate exporting and inspecting ChatML/ShareGPT JSONL.

## 6. Code Quality & Compliance
- [x] Ensure all code changes are PEP-8 compliant.
- [x] Run full test suite and fix any failures.
- [x] Validate with pycodestyle and other linters.


---

**Notes:**
- Reference: [Unsloth Chat Templates Documentation](https://docs.unsloth.ai/basics/chat-templates)
- All output files must be directly usable with Unsloth's chat_template reformatter, with no manual editing required.
- Consider adding a test script to validate output files against Unsloth's expected formats.

---

**End of Plan**
