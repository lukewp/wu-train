# wu-train


This project processes and parses the full lyrics of the Wu-Tang Clan and affiliates, using a static copy of the @mathisve/wu-tang-clan-lyrics-dataset (included as a subfolder for stability). The goal is to extract, organize, and prepare lyrics by individual performer, enabling the creation of fine-tuning datasets for large language models (LLMs) that can generate lyrics in the style of each Wu-Tang member.

**Dataset Handling:**
- The dataset is included directly in this repository as `wu-tang-clan-lyrics-dataset/` to ensure long-term stability and reproducibility, even if the upstream source changes or disappears.
- Updates to the dataset are performed manually and only as needed. If the upstream dataset is updated, changes can be pulled and the code refactored as necessary.

**Development Approach:**
- The codebase is built using a test-driven development (TDD) workflow, with modular, well-documented Python code and a comprehensive test suite.


## Features
- Parses raw lyrics labeled by performer (e.g., `[raekwon]`, `[meth]`, etc.)
- Canonicalizes performer names and handles aliases
- Filters out non-performer and structural labels (e.g., `[chorus]`, `[2x]`, `[all]`)
- Concatenates and saves all lyrics for each performer into separate files in `out/`
- Allows output for all performers or a specific performer
- Prepares data for LLM fine-tuning or analysis
- Includes a reproducible Python development environment via devcontainer


## Usage
1. Open the project in a devcontainer (VS Code recommended)
2. Run the provided Python scripts to process and split the lyrics by performer:
   - `python -m src.split_lyrics_by_performer` (see script help for options)
3. Use the generated files in `out/` for LLM fine-tuning or further NLP tasks

## Requirements
- Python 3.11+
- See `requirements.txt` for dependencies (installed automatically in the devcontainer)


## Dataset
Source: [@mathisve/wu-tang-clan-lyrics-dataset](https://github.com/mathisve/wu-tang-clan-lyrics-dataset)

**Note:** The dataset is included as a static subfolder. If the upstream dataset is updated, you may update the subfolder and refactor as needed.


## License
see `LICENSE.md`
