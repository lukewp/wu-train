# =============================================================================
# split_lyrics_by_performer.py
#
# This module provides core utilities for parsing, normalizing, and classifying
# section keys in Wu-Tang Clan and affiliate lyrics datasets. It enables robust
# extraction and canonicalization of performer labels, filtering of non-performer
# sections, and preparation of data for LLM training or analysis.
#
# Main Features:
# - extract_key_candidates_from_lines: Extract and normalize [xxx] keys from lyrics lines.
# - normalize_key_string: Consistent normalization of key strings for comparison and classification.
# - match_key_to_canonical: Map aliases to canonical performer names using a provided alias map.
# - classify_key: Classify keys as 'performer', 'ignore', or 'skip' using alias and ignore sets.
# - IGNORE_SET: Comprehensive set of non-performer/structural labels to filter out.
# - load_lyrics_file: Utility for reading lyrics files with error handling.
#
# This module is designed for use in data cleaning, preprocessing, and test-driven
# workflows for lyric-based machine learning and analysis projects.
# =============================================================================

# 1. Imports
import re
import os
from typing import List, Dict, Set, Optional

 # 2. Constants
IGNORE_SET: Set[str] = set([
    "skit", "interlude", "chorus", "bridge", "intro", "outro", "instrumental", "crowd", "audience", "refrain",
    "dj", "mc", "beat", "music", "sound", "applause", "laughing", "noise", "verse", "break", "hook", "only", "chrous",
    "2x", "3x", "4x", "5x", "6x", "x2", "x3", "x4", "x5", "x6", "first", "second", "last", "repeat", "both",
    "1", "2", "3", "4", "5", "6", "7", "one", "two", "three", "four", "five", "six", "seven", 
    "*sound of bomb dropping*", "15 seconds of instrumental", "35 seconds of instrumental pass until the martial arts samples",
    "instrumental for 40 seconds", "instrumental for the first 11 seconds", "music", "fades", "in", "out",
    "changes", "drops", "switch", "bees", "beez", "buzzing", "bell rings", "last", "line", "lines", "latter",
    "coughing", "dogs barking", "eerie winds blowing", "glasses jewelry tinkling", "gong bangs", "gun blast", "gunblast", "gunshot",
    "rocket fired whistles off and explodes breaking glass", "skip next line on the second time of chorus",
    "sound of a plane crashing and explosion", "sounds of combat", "sounds of fighting", "swords clash",
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
        trim_chars (list of str, optional): Characters to treat as separators (replace with space, e.g., ':').
        replace_with_space_chars (list of str, optional): Characters to replace with whitespace (e.g., '&', '/').

    Returns:
        list of str: Cleaned keys found in the input lines, lowercased and whitespace-normalized.
    """
    if trim_chars is None:
        trim_chars = [':']
    if replace_with_space_chars is None:
        replace_with_space_chars = ['&', '/', '+', '-', '(', ')']
    key_pattern = re.compile(r'^\[([^\]]+)\]$')
    keys = []
    for line in lines:
        match = key_pattern.match(line.strip())
        if match:
            key = match.group(1)
            # Use normalize_key_string for normalization
            key = normalize_key_string(key, trim_chars=trim_chars, replace_with_space_chars=replace_with_space_chars)
            keys.append(key)
    return keys

# 4. Domain-Specific Functions
def match_key_to_canonical(
    key: str,
    alias_map: Dict[str, List[str]]
) -> Optional[str]:
    """
    Given a key (already cleaned/lowercased), return the canonical performer name from alias_map,
    or None if not found.

    Args:
        key (str): Cleaned key to look up (e.g., 'rza', 'bobby digital').
        alias_map (dict): Mapping of canonical_name -> list of aliases.

    Returns:
        str or None: Canonical performer name if found, else None.
    """
    key_norm = key.strip().lower()
    for canonical, aliases in alias_map.items():
        for alias in aliases:
            if key_norm == alias.strip().lower():
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
    # 1. Check for performer alias as whole word
    for aliases in alias_map.values():
        for alias in aliases:
            alias_lc = alias.lower()
            if f' {alias_lc} ' in f' {key_norm} ':
                return 'performer'

    # 2. Check for ignore: full-string match first
    if key_norm in ignore_set:
        return 'ignore'
    # 3. Check for ignore: if all words in key_norm are in ignore_set, ignore; else, skip
    words = [w for w in key_norm.split() if w.strip()]
    if words and all(w in ignore_set for w in words):
        return 'ignore'
    # 4. Otherwise, skip
    return 'skip'

# Helper: normalize a single key string using the same logic as extract_key_candidates_from_lines
def normalize_key_string(
    key: str,
    trim_chars: Optional[List[str]] = None,
    replace_with_space_chars: Optional[List[str]] = None
) -> str:
    if trim_chars is None:
        trim_chars = [':']
    if replace_with_space_chars is None:
        replace_with_space_chars = ['&', '/', '+', '-', '(', ')', ',']
    all_replace = list(set((replace_with_space_chars or []) + (trim_chars or [])))
    # Remove brackets if present
    key = key.strip()
    if key.startswith('[') and key.endswith(']'):
        key = key[1:-1]
    # Replace all separators with space
    for c in all_replace:
        key = key.replace(c, ' ')
    # Iteratively replace double spaces with single space
    while '  ' in key:
        key = key.replace('  ', ' ')
    # Normalize whitespace, lowercase, strip
    key = ' '.join(key.split()).lower().strip()
    return key


# 5. File I/O Functions
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


# 6. CLI Entry Point
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Default file path
    default_path = Path(__file__).parent.parent / "wu-tang-clan-lyrics-dataset" / "wu-tang.txt"
    if len(sys.argv) > 1:
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
    keys = extract_key_candidates_from_lines(lines)
    print(f"Extracted {len(keys)} keys:")
    for k in keys:
        print(k)