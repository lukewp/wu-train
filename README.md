# wu-train


This project processes and parses the full lyrics of the Wu-Tang Clan and affiliates, using a static copy of the @mathisve/wu-tang-clan-lyrics-dataset (included as a subfolder for stability). The goal is to extract, organize, and prepare lyrics by individual performer, enabling the creation of fine-tuning datasets for large language models (LLMs) that can generate lyrics in the style of each Wu-Tang member.

## Key Features & Improvements
- **Robust Normalization:** Consistent normalization of performer keys, including whitespace, separators, and alias mapping.
- **Alias Handling:** Canonicalizes performer names and supports flexible alias mapping via `src/performer_aliases.json`.
- **Ignore Logic:** Filters out non-performer and structural labels (e.g., `[chorus]`, `[2x]`, `[all]`) using a comprehensive ignore set.
- **Test-Driven Development:** Comprehensive test suite covering all major features, including integration and PEP-8 compliance checks.
- **DRY & Documented Code:** Modular, DRY Python code with type hints and clear documentation throughout.
- **CLI Usage:** Run the main script directly or via CLI, with options for input file, output directory, and performer selection.
- **Extensible:** Easily add new performers/aliases or update ignore logic by editing the relevant JSON/config files.

**Dataset Handling:**
- The dataset is included directly in this repository as `wu-tang-clan-lyrics-dataset/` to ensure long-term stability and reproducibility, even if the upstream source changes or disappears.
- Updates to the dataset are performed manually and only as needed. If the upstream dataset is updated, changes can be pulled and the code refactored as necessary.

**Development Approach:**
- The codebase is built using a test-driven development (TDD) workflow, with modular, well-documented Python code and a comprehensive test suite.

## CLI Usage
You can run the main script directly from the command line:

```bash
python -m src.split_lyrics_by_performer [input_file] [output_dir]
```

Options:
- `input_file`: Path to the lyrics file (default: `wu-tang-clan-lyrics-dataset/wu-tang.txt`)
- `output_dir`: Directory to write performer files (default: `out/`)

You can also specify a particular performer or alias for targeted output (see script help for details).


## Features
- Parses raw lyrics labeled by performer (e.g., `[raekwon]`, `[meth]`, etc.)
- Canonicalizes performer names and handles aliases
- Filters out non-performer and structural labels (e.g., `[chorus]`, `[2x]`, `[all]`)
- Concatenates and saves all lyrics for each performer into separate files in `out/`
- Allows output for all performers or a specific performer
- Prepares data for LLM fine-tuning or analysis
- Includes a reproducible Python development environment via devcontainer

- Comprehensive test suite for all major features and integration
- PEP-8 compliance checks for code quality


## Usage
1. Open the project in a devcontainer (VS Code recommended)
2. Run the provided Python scripts to process and split the lyrics by performer:
   - `python -m src.split_lyrics_by_performer` (see script help for options)
3. Use the generated files in `out/` for LLM fine-tuning or further NLP tasks

### Running Tests
To run all tests and check code quality:

```bash
python -m unittest discover tests
```

PEP-8 compliance is checked automatically in the test suite.

## Requirements
- Python 3.11+
- See `requirements.txt` for dependencies (installed automatically in the devcontainer)

## Extending & Customizing
- **Add Performers/Aliases:** Edit `src/performer_aliases.json` to add new canonical names or aliases.
- **Update Ignore Logic:** Modify the `IGNORE_SET` in `src/split_lyrics_by_performer.py` to change which labels are ignored.


## Dataset
Source: [@mathisve/wu-tang-clan-lyrics-dataset](https://github.com/mathisve/wu-tang-clan-lyrics-dataset)

**Note:** The dataset is included as a static subfolder. If the upstream dataset is updated, you may update the subfolder and refactor as needed.


## License
see `LICENSE.md`
