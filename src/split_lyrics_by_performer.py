# =============================================================================
# split_lyrics_by_performer.py
#
# This module provides core utilities for parsing, normalizing, and classifying
# section keys in Wu-Tang Clan and affiliate lyrics datasets. It enables robust
# extraction and canonicalization of performer labels, filtering of non-
# performer sections, and preparation of data for LLM training or analysis.
#
# Main Features:
# - extract_key_candidates_from_lines: Extract and normalize [xxx] keys from
#   lyrics lines.
# - normalize_key_string: Consistent normalization of key strings for
#   comparison and classification.
# - match_key_to_canonical: Map aliases to canonical performer names using a
#   provided alias map.
# - classify_key: Classify keys as 'performer', 'ignore', or 'skip' using alias
#   and ignore sets.
# - IGNORE_SET: Comprehensive set of non-performer/structural labels to filter
#   out.
# - load_lyrics_file: Utility for reading lyrics files with error handling.
#
# This module is designed for use in data cleaning, preprocessing, and test-
#   driven workflows for lyric-based machine learning and analysis projects.
# =============================================================================

__all__ = [
    'extract_key_candidates_from_lines',
    'normalize_key_string',
    'match_key_to_canonical',
    'classify_key',
    'find_canonical_performers',
    'split_lyrics_by_performer',
    'write_performer_files',
    'write_performer_jsonl',
    'split_lines_to_jsonl_pairs',
    'load_lyrics_file',
    'IGNORE_SET',
]

# 1. Imports
import re
import os
from typing import List, Dict, Set, Optional
import json

# 2. Constants

# Characters treated as separators and trimmed during key normalization
DEFAULT_TRIM_CHARS: List[str] = [':']

# Characters replaced with spaces during key normalization
DEFAULT_REPLACE_WITH_SPACE_CHARS: List[str] = [
    '&', '/', '+', '-', '(', ')', ','
]

IGNORE_SET: Set[str] = set([
    "skit", "interlude", "chorus", "bridge", "intro", "outro", "instrumental",
    "crowd", "audience", "refrain", "dj", "mc", "beat", "music", "sound",
    "applause", "laughing", "noise", "verse", "break", "hook", "only",
    "2x", "3x", "4x", "5x", "6x", "x2", "x3", "x4", "x5", "x6",
    "first", "second", "last", "repeat", "both",
    "1", "2", "3", "4", "5", "6", "7",
    "one", "two", "three", "four", "five", "six", "seven",
    "*sound of bomb dropping*", "15 seconds of instrumental", "chrous",
    "35 seconds of instrumental pass until the martial arts samples",
    "instrumental for 40 seconds", "instrumental for the first 11 seconds",
    "music", "fades", "in", "out", "changes", "drops", "switch", "bees",
    "beez", "buzzing", "bell rings", "last", "line", "lines", "latter",
    "coughing", "dogs barking", "eerie winds blowing", "swords clash",
    "glasses jewelry tinkling", "gong bangs", "gun blast", "gunblast",
    "gunshot", "rocket fired whistles off and explodes breaking glass",
    "skip next line on the second time of chorus", "sounds of fighting",
    "sound of a plane crashing and explosion", "sounds of combat"
])


# 3. Core Utility Functions
def extract_key_candidates_from_lines(
    lines: List[str],
    trim_chars: Optional[List[str]] = None,
    replace_with_space_chars: Optional[List[str]] = None
) -> List[str]:
    """
    Extract and clean all [xxx] key patterns from a list of lines.

    Args:
        lines (list of str): Lines of lyrics to scan for [xxx] keys.
        trim_chars (list of str, optional): Characters to treat as separators
            (replace with space, e.g., ':').
        replace_with_space_chars (list of str, optional): Characters to replace
            with whitespace (e.g., '&', '/').

    Returns:
        list of str: Cleaned keys found in the input lines, lowercased and
            whitespace-normalized.
    """
    if trim_chars is None:
        trim_chars = DEFAULT_TRIM_CHARS
    if replace_with_space_chars is None:
        # Use a subset for extraction (no comma)
        replace_with_space_chars = DEFAULT_REPLACE_WITH_SPACE_CHARS[:-1]
    key_pattern = re.compile(r'^\[([^\]]+)\]$')
    keys = []
    for line in lines:
        match = key_pattern.match(line.strip())
        if match:
            key = match.group(1)
            # Use normalize_key_string for normalization
            key = normalize_key_string(
                key,
                trim_chars=trim_chars,
                replace_with_space_chars=replace_with_space_chars
            )
            keys.append(key)
    return keys


# Helper: normalize whitespace (replace multiple spaces with a single space)
def normalize_whitespace(s: str) -> str:
    """
    Replace multiple consecutive whitespace characters in a string with a
    single space. Ensures consistent spacing for normalization and comparison.

    Args:
        s (str): Input string to normalize.
    Returns:
        str: String with normalized whitespace.
    """
    return re.sub(r'\s+', ' ', s)


# 4. Domain-Specific Functions
def match_key_to_canonical(
    key: str,
    alias_map: Dict[str, List[str]]
) -> Optional[str]:
    """
    Given a key (already cleaned/lowercased), return the canonical performer
      name from alias_map, or None if not found.

    Args:
        key (str): Cleaned key to look up (e.g., 'rza', 'bobby digital').
        alias_map (dict): Mapping of canonical_name -> list of aliases.

    Returns:
        str or None: Canonical performer name if found, else None.
    """
    key_norm = normalize_key_string(key)
    for canonical, aliases in alias_map.items():
        for alias in aliases:
            alias_norm = normalize_key_string(alias)
            if key_norm == alias_norm:
                return canonical
    return None


def classify_key(
    key: str,
    alias_map: Dict[str, List[str]],
    ignore_set: Set[str] = IGNORE_SET
) -> str:
    """
    Classify a key as 'performer', 'ignore', or 'skip'.
    Args:
        key (str): The key to classify (should be lowercased and cleaned).
        alias_map (dict): Mapping of canonical_name -> list of aliases.
        ignore_set (set): Set of keys to ignore.
    Returns:
        str: 'performer', 'ignore', or 'skip'.
    """
    key_norm = normalize_key_string(key)
    # 1. Check for performer alias as whole word (normalized)
    for aliases in alias_map.values():
        for alias in aliases:
            alias_norm = normalize_key_string(alias)
            if f' {alias_norm} ' in f' {key_norm} ':
                return 'performer'

    # 2. Check for ignore: full-string match first
    if key_norm in ignore_set:
        return 'ignore'
    # 3. Check for ignore: if all words in key_norm are in ignore_set, ignore;
    #    else, skip
    words = [w for w in key_norm.split() if w.strip()]
    if words and all(w in ignore_set for w in words):
        return 'ignore'
    # 4. Otherwise, skip
    return 'skip'


# Helper: normalize a single key string using the same logic as
#   extract_key_candidates_from_lines
def normalize_key_string(
    key: str,
    trim_chars: Optional[List[str]] = None,
    replace_with_space_chars: Optional[List[str]] = None
) -> str:
    if trim_chars is None:
        trim_chars = DEFAULT_TRIM_CHARS
    if replace_with_space_chars is None:
        replace_with_space_chars = DEFAULT_REPLACE_WITH_SPACE_CHARS
    all_replace = list(set(
        (replace_with_space_chars or []) +
        (trim_chars or [])
    ))
    # Remove brackets if present
    key = key.strip()
    if key.startswith('[') and key.endswith(']'):
        key = key[1:-1]
    # Replace all separators with space
    for c in all_replace:
        key = key.replace(c, ' ')
    # Normalize whitespace (multiple spaces to single)
    key = normalize_whitespace(key)
    # Lowercase and strip
    key = key.lower().strip()
    return key


# Helper: find all canonical performers matching a normalized key string
def find_canonical_performers(
    key_norm: str,
    alias_map: Dict[str, List[str]]
) -> Set[str]:
    """
    Given a normalized key string and alias map, return all matching canonical
     performer names. Matches both whole-word aliases and per-part
     (split by spaces) to maximize robust performer attribution.
    """
    performers = set()
    for canonical, aliases in alias_map.items():
        for alias in aliases:
            alias_norm = normalize_key_string(alias)
            if f' {alias_norm} ' in f' {key_norm} ':
                performers.add(canonical)
    for part in key_norm.split():
        canonical = match_key_to_canonical(part, alias_map)
        if canonical:
            performers.add(canonical)
    return performers


# 5. Section Attribution Logic
def split_lyrics_by_performer(
    lines: List[str],
    alias_map: Dict[str, List[str]],
    ignore_set: Set[str] = IGNORE_SET
) -> Dict[str, List[str]]:
    """
    Process lyrics lines, attributing text chunks to performers and skipping
      lines after ignore/skip keys.
    Args:
        lines: List of lyric lines (including [key] lines).
        alias_map: Mapping of canonical performer names to aliases.
        ignore_set: Set of keys to ignore.
    Returns:
        Dict of performer name -> list of attributed lines.
    """
    performer_chunks: Dict[str, List[str]] = {
        c: [] for c in alias_map
    }
    current_mode = None  # 'performer', 'ignore', 'skip', or None
    current_performers = []  # List of canonical performer names

    for line in lines:
        # Check for [key] line
        key_match = re.match(r'^\[([^\]]+)\]$', line.strip())
        if key_match:
            key_raw = key_match.group(1)
            key_norm = normalize_key_string(key_raw)
            key_type = classify_key(key_norm, alias_map, ignore_set)
            # Always reset mode and performers on new key
            if key_type == 'performer':
                performers = find_canonical_performers(key_norm, alias_map)
                # If more than one performer, treat as skip
                if len(performers) > 1:
                    current_mode = 'skip'
                    current_performers = []
                elif len(performers) == 1:
                    current_mode = 'performer'
                    current_performers = list(performers)
                else:
                    current_mode = None
                    current_performers = []
            elif key_type == 'ignore':
                current_mode = 'ignore'
                current_performers = []
            elif key_type == 'skip':
                current_mode = 'skip'
                current_performers = []
            else:
                current_mode = None
                current_performers = []
            continue  # Don't attribute key lines themselves

        # Non-key line
        if current_mode == 'performer' and current_performers:
            for performer in current_performers:
                performer_chunks[performer].append(line)
        # If ignore or skip, do not attribute
        # If current_mode is None, do not attribute

    return performer_chunks


# Helper: split lines into JSONL prompt/completion pairs based on verse breaks
def split_lines_to_jsonl_pairs(
    lines: List[str],
    prompt_sep: str = " ++++",
    completion_stop: str = " ####"
) -> List[Dict[str, str]]:
    """
    Given a list of lyric lines, split into prompt/completion pairs for
     LLM fine-tuning. Each prompt is a line, and the completion is the next
     line, with verse breaks (empty lines) resetting the pairing. Only pairs
     that do not cross verse breaks are included.
    Args:
        lines: List of lyric lines (may include empty lines for verse breaks).
        prompt_sep: String to append to the prompt (default: ' ++++').
        completion_stop: String to append to the completion (default: ' ####').
    Returns:
        List of dicts with 'prompt' and 'completion' keys.
    """
    pairs = []
    # Split into blocks (verses) separated by empty lines
    block = []
    for line in lines:
        if line.strip() == '':
            if block:
                # Pair every consecutive line in the block
                for i in range(len(block) - 1):
                    prompt = block[i].strip() + prompt_sep
                    completion = ' ' + block[i+1].strip() + completion_stop
                    pairs.append({"prompt": prompt, "completion": completion})
                block = []
        else:
            block.append(line)
    # Process any trailing block
    if block:
        for i in range(len(block) - 1):
            prompt = block[i].strip() + prompt_sep
            completion = ' ' + block[i+1].strip() + completion_stop
            pairs.append({"prompt": prompt, "completion": completion})
    return pairs


# 6. Output Functions
def write_performer_files(
    performer_chunks: Dict[str, List[str]],
    out_dir: str,
    alias_map: Optional[Dict[str, List[str]]] = None
) -> None:
    """
    Write each performer's lyrics to a file in the output directory.
    Only valid performer keys (present in alias_map) are written.
    Args:
        performer_chunks: Dict of performer name -> list of lines.
        out_dir: Output directory path.
        alias_map: Optional dict of canonical performer names -> aliases.
            If provided, only write files for these keys.
    """
    os.makedirs(out_dir, exist_ok=True)
    valid_performers = set(performer_chunks.keys())
    if alias_map is not None:
        valid_performers = set(alias_map.keys())
    for performer, lines in performer_chunks.items():
        if alias_map is not None and performer not in valid_performers:
            continue
        safe_name = ''.join(
            c if c.isalnum() or c in (' ', '_') else '_'
            for c in performer
        ).replace(' ', '_')
        out_path = os.path.join(out_dir, f"{safe_name}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")


def write_performer_jsonl(
    performer_chunks: Dict[str, List[str]],
    out_dir: str,
    alias_map: Optional[Dict[str, List[str]]] = None,
    prompt_sep: str = " ++++",
    completion_stop: str = " ####"
) -> None:
    """
    Write each performer's lyrics as JSONL prompt/completion pairs for LLM
     fine-tuning. Each prompt is a verse (split by double newlines), and the
     completion is the next verse.
    Args:
        performer_chunks:   Dict of performer name -> list of lines.
        out_dir:            Output directory path.
        alias_map:          Optional dict of canonical performer
                              names -> aliases.
        prompt_sep:         Separator to end the prompt (default: ' ++++').
        completion_stop:    Stop sequence to end the completion
                              (default: ' ####').
    """
    os.makedirs(out_dir, exist_ok=True)
    valid_performers = set(performer_chunks.keys())
    if alias_map is not None:
        valid_performers = set(alias_map.keys())
    for performer, lines in performer_chunks.items():
        if alias_map is not None and performer not in valid_performers:
            continue
        safe_name = ''.join(
            c if c.isalnum() or c in (' ', '_') else '_'
            for c in performer
        ).replace(' ', '_')
        out_path = os.path.join(out_dir, f"{safe_name}.jsonl")
        pairs = split_lines_to_jsonl_pairs(
            lines,
            prompt_sep=prompt_sep,
            completion_stop=completion_stop
        )
        with open(out_path, "w", encoding="utf-8") as f:
            for obj in pairs:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_lyrics_file(filepath: str) -> str:
    """
    Load and return the full contents of the lyrics file as a string.

    Args:
        filepath (str): Path to the lyrics file.

    Returns:
        str: Full contents of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


# 7. CLI Entry Point
if __name__ == "__main__":
    import sys
    from pathlib import Path

    help_text = f"""
Usage:
    python -m src.split_lyrics_by_performer [input_file] [output_dir]
                                            [performer_or_alias] [--jsonl]

Arguments:
    input_file         Path to lyrics file
                         (default: wu-tang-clan-lyrics-dataset/wu-tang.txt)

    output_dir         Directory to write performer files (default: out/)

    performer_or_alias (optional) Only output the file for the specified
                         performer or alias (e.g., rza, ghost, raekwon)

    --jsonl            (optional) Export as JSONL prompt/completion pairs for
                         LLM fine-tuning

Examples:
    python -m src.split_lyrics_by_performer
    python -m src.split_lyrics_by_performer wu-tang.txt out rza
    python -m src.split_lyrics_by_performer wu-tang.txt out "tony starks"
    python -m src.split_lyrics_by_performer wu-tang.txt out --jsonl
    python -m src.split_lyrics_by_performer wu-tang.txt out rza --jsonl
"""
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(help_text)
        sys.exit(0)

    # Default file path
    default_path = (
        Path(__file__).parent.parent /
        "wu-tang-clan-lyrics-dataset" /
        "wu-tang.txt"
    )
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        lyrics_path = Path(sys.argv[1])
    else:
        lyrics_path = default_path

    print(f"Loading lyrics from: {lyrics_path}")
    try:
        text = load_lyrics_file(str(lyrics_path))
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

    lines = text.splitlines()

    # Load alias map
    alias_path = Path(__file__).parent / "performer_aliases.json"
    try:
        with open(alias_path, 'r', encoding='utf-8') as f:
            alias_map = json.load(f)
    except Exception as e:
        print(f"Error loading alias map: {e}")
        sys.exit(1)

    # Run performer attribution
    performer_chunks = split_lyrics_by_performer(lines, alias_map, IGNORE_SET)

    # Output directory (default: 'out')
    if len(sys.argv) > 2 and not sys.argv[2].startswith('-'):
        out_dir = sys.argv[2]
    else:
        out_dir = str(Path(__file__).parent.parent / "out")

    # Check for --jsonl option
    jsonl_mode = any(arg == "--jsonl" for arg in sys.argv[1:])

    # Optional: performer or alias filter
    performer_arg = None
    if len(sys.argv) > 3 and not sys.argv[3].startswith('-'):
        performer_arg = sys.argv[3]

    if performer_arg:
        canonical = match_key_to_canonical(performer_arg, alias_map)
        if canonical is None:
            print(f"Error: Performer or alias '{performer_arg}' "
                  f"not found in alias map.")
            sys.exit(1)
        filtered_chunks = {canonical: performer_chunks.get(canonical, [])}
        if jsonl_mode:
            print(f"Writing JSONL file for performer: {canonical} "
                  f"to {out_dir}")
            write_performer_jsonl(filtered_chunks,
                                  out_dir,
                                  alias_map=alias_map)
            print(f"Done. File written: {canonical}.jsonl")
        else:
            print(f"Writing file for performer: {canonical} to {out_dir}")
            write_performer_files(filtered_chunks,
                                  out_dir,
                                  alias_map=alias_map)
            print(f"Done. File written: {canonical}.txt")
    else:
        if jsonl_mode:
            print(f"Writing JSONL files for all performers to: {out_dir}")
            write_performer_jsonl(performer_chunks,
                                  out_dir,
                                  alias_map=alias_map)
            print(f"Done."
                  f" {len([k for k in performer_chunks if k in alias_map])} "
                  "JSONL files written.")
        else:
            print(f"Writing performer files to: {out_dir}")
            write_performer_files(
                performer_chunks, out_dir, alias_map=alias_map
            )
            print(f"Done."
                  f" {len([k for k in performer_chunks if k in alias_map])} "
                  "performer files written.")
