# wu-train v1.0: transforming Wu-Tang Clan verses to LLM training sets


This project processes and parses the full lyrics of the Wu-Tang Clan and affiliates, using a static copy of the @mathisve/wu-tang-clan-lyrics-dataset (included as a subfolder for stability). The goal is to extract, organize, and prepare lyrics by individual performer, enabling the creation of fine-tuning datasets for large language models (LLMs) that can generate lyrics in the style of each Wu-Tang member.

## Purpose
This project is intended for educational use only, to help people learn how to train LLMs from preexisting content. It's important for users to respect copyright and other relevant intellectual property laws when adapting this code for any production use.

## Key Features & Improvements
- **Robust Normalization:** Consistent normalization of performer keys, including whitespace, separators, and alias mapping.
- **Alias Handling:** Canonicalizes performer names and supports flexible alias mapping via `src/performer_aliases.json`.
- **Ignore Logic:** Filters out non-performer and structural labels (e.g., `[chorus]`, `[2x]`, `[all]`) using a comprehensive ignore set.
- **Test-Driven Development:** Comprehensive test suite covering all major features, including integration and PEP-8 compliance checks.
- **DRY & Documented Code:** Modular, DRY Python code with type hints and clear documentation throughout.
- **CLI Usage:** Run the main script directly or via CLI, with options for input file, output directory, and performer selection.
- **Extensible:** Easily add new performers/aliases or update ignore logic by editing the relevant JSON/config files.

**Dataset Handling:**
- The Wu Tang Clan Lyrics Dataset is meant to be included directly in the root of this repository as `./wu-tang-clan-lyrics-dataset/`.
- Updates to the dataset are performed manually and only as needed. If the upstream dataset is updated, changes can be pulled and the code refactored as necessary.

**Development Approach:**
- The codebase is built using a test-driven development (TDD) workflow, with modular, well-documented Python code and a comprehensive test suite.

## JSONL Output for LLM Fine-Tuning

You can export each performer's lyrics as JSONL files for LLM fine-tuning in Unsloth-compatible formats:

- **ChatML** (default, recommended for Unsloth and multiplatform workflows)
- **ShareGPT** (compatible with OpenChat and Unsloth)

**To generate ChatML JSONL files:**

```bash
python -m src.split_lyrics_by_performer wu-tang-clan-lyrics-dataset/wu-tang.txt out --chatml
```

**To generate ShareGPT JSONL files:**

```bash
python -m src.split_lyrics_by_performer wu-tang-clan-lyrics-dataset/wu-tang.txt out --sharegpt
```

**To generate JSONL for a specific performer:**

```bash
python -m src.split_lyrics_by_performer wu-tang-clan-lyrics-dataset/wu-tang.txt out --performer rza --chatml
```

**ChatML JSONL Format Example:**

```json
{"conversations": [
    {"role": "system", "content": "You are Wu-Tang Clan member rza. When a user prompts you with one of your lyrics, you deliver the next line."},
    {"role": "user", "content": "yo, you may catch me in a pair of polo skipperys, matching cap"},
    {"role": "assistant", "content": "razor blades in my gums (bobby!)"}
]}
```

**ShareGPT JSONL Format Example:**

```json
[
   {"from": "system", "value": "You are Wu-Tang Clan member rza. When a user prompts you with one of your lyrics, you deliver the next line."},
   {"from": "human", "value": "yo, you may catch me in a pair of polo skipperys, matching cap"},
   {"from": "gpt", "value": "razor blades in my gums (bobby!)"}
]
```

---

You can run the main script directly from the command line:

```bash
python -m src.split_lyrics_by_performer [input_file] [output_dir] [--chatml|--sharegpt] [--performer name]
```

Options:
- `input_file`: Path to the lyrics file (default: `wu-tang-clan-lyrics-dataset/wu-tang.txt`)
- `output_dir`: Directory to write performer files (default: `out/`)
- `--chatml`: Export ChatML format (Unsloth default, recommended)
- `--sharegpt`: Export ShareGPT format (OpenChat/Unsloth compatible)
- `--performer name`: *(optional)* Only output for the specified performer or alias (case-insensitive, e.g., `rza`, `bobby digital`, `ghostface`)

**Examples:**

Output all performers (ChatML, default):
```bash
python -m src.split_lyrics_by_performer
```

Output only RZA's lyrics (ChatML):
```bash
python -m src.split_lyrics_by_performer wu-tang-clan-lyrics-dataset/wu-tang.txt out --performer rza --chatml
```

Output only Ghostface's lyrics (using an alias, ShareGPT):
```bash
python -m src.split_lyrics_by_performer wu-tang-clan-lyrics-dataset/wu-tang.txt out --performer tony starks --sharegpt
```

---

**Note:** For custom LLM formats, use [Unsloth's chat_template reformatter](https://github.com/unslothai/unsloth) as middleware to convert ChatML/ShareGPT output to your target format. This workflow is multiplatform and recommended for most LLM fine-tuning pipelines. An implementation on how to do this using Google's Colab is in the `wu_train_colab.ipynb` file in the repo root.


## Features
- Parses raw lyrics labeled by performer (e.g., `[raekwon]`, `[meth]`, etc.)
- Canonicalizes performer names and handles aliases
- Filters out non-performer and structural labels (e.g., `[chorus]`, `[2x]`, `[all]`)
- Concatenates and saves all lyrics for each performer into separate files in `out/`
- Exports each performer's lyrics as JSONL for LLM fine-tuning (`--chatml` or `--sharegpt`)
- Allows output for all performers or a specific performer
- Prepares data for LLM fine-tuning or analysis
- Includes a reproducible Python development environment via devcontainer
- Comprehensive test suite for all major features and integration
- PEP-8 compliance checks for code quality


## Usage

1. Open the project in a devcontainer (VS Code recommended)
2. If the `wu-tang-clan-lyrics-dataset/` folder is missing or you want to update it, you can clone the upstream dataset, then setting to the commit from which this repo was built:
   ```bash
   git clone https://github.com/mathisve/wu-tang-clan-lyrics-dataset.git wu-tang-clan-lyrics-dataset

   cd wu-tang-clan-lyrics-dataset

   git reset --hard 5572a1e0150a6c10b927da049415dc20a359ba03
   ```
   (Or update the folder as needed.)
3. For interactive exploration, open `interactive_lyrics_lookup.ipynb` and enter a performer or alias to view their lyrics directly in the notebook.
4. To process and split the lyrics by performer via script:
   - Run `python -m src.split_lyrics_by_performer` (see script help for options)
   - Add `--chatml` or `--sharegpt` to export JSONL for each performer
5. Use the generated files in `out/` for LLM fine-tuning or further NLP tasks

### Example Output
Below is an example extract of what would appear in `out/rza.txt`:

```text
yo, you may catch me in a pair of polo skipperys, matching cap
razor blades in my gums (bobby!)
you may catch me in yellow havana joe's goose jumper
and my phaser off stun (bobby!)
y'all might just catch me in the park playin chess, studyin math
signin 7 and a sun (bobby!)
but you won't catch me without the ratchet, in the joint
smoked out, dead broke or off point (bobby!)

tempted by the sins of life, the pleasures of lust
with wild imaginings that you can't discuss
oh, the flesh is weak, it's a struggle for feast
it's a daily conflict between man and beast
we, strive for god, and a better tomorrow
still suffering, from the unforgettable sorrow
repent from thy sins, son, and walk these straight
stop talking all that trash, boy, and spark these straight
evicted by the pressures of life, at every vital point
still, i wouldn't give an oint'
or, flinch an inch, or pitch a pinch
off the pie, or every try to try your winch
confronted by the devil himself, and stay strong
you think you can take the king, now meet kong
strong as the base of a mountain, there's no counting
how many mc's, have sprung from our fountain
```

and `out/rza.jsonl` (if `--chatml` is used in the CLI):
```json
{"conversations": [{"role": "system", "content": "You are Wu-Tang Clan member rza. When a user prompts you with one of your lyrics, you deliver the next line."}, {"role": "user", "content": "yo, you may catch me in a pair of polo skipperys, matching cap"}, {"role": "assistant", "content": "razor blades in my gums (bobby!)"}]}
```

Below is an example extract of what would appear in `out/inspectah_deck.txt`:

```text
well i'm a sire, i set the microphone on fire
rap styles vary, and carry like mariah
i come from the shaolin slum, and the isle i'm from
is coming through with nuff niggas and nuff guns
so if you wanna come sweating, stressing, contesting
you'll catch a sharp sword to the midsection
don't talk the talk, if you can't walk the walk
phony niggas are outlined in chalk
a man vexed, is what the projects made me
rebel to the grain there's no way to barricade me
steamrolling niggas like a eighteen wheeler
with the drunk driver driving, there's no surviving
```

and `out/inspectah_deck.jsonl` (if `--chatml` is used in the CLI):
```json
{"conversations": [{"role": "system", "content": "You are Wu-Tang Clan member inspectah deck. When a user prompts you with one of your lyrics, you deliver the next line."}, {"role": "user", "content": "well i'm a sire, i set the microphone on fire"}, {"role": "assistant", "content": "rap styles vary, and carry like mariah"}]}
```

### Running Tests
To run all tests and check code quality:

```bash
pytest

# OR:

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
**Use at your own risk. Notably, OpenAI will not allow an LLM to be fine-tuned with this dataset because the content triggers the "hate" flag. BUT in general, unless you have explicit permission from the Wu-Tang Clan, you don't have the rights to use this data to fine-tune an LLM.**

see `LICENSE.md`
