import re
import os

def extract_key_candidates_from_lines(
    lines,
    trim_chars=None,
    replace_with_space_chars=None
):
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
        replace_with_space_chars = ['&', '/']
    # Merge trim_chars into replace_with_space_chars, deduplicated
    all_replace = list(set((replace_with_space_chars or []) + (trim_chars or [])))
    key_pattern = re.compile(r'^\[([^\]]+)\]$')
    keys = []
    for line in lines:
        match = key_pattern.match(line.strip())
        if match:
            key = match.group(1)
            # Replace all separators with space
            for c in all_replace:
                key = key.replace(c, ' ')
            # Iteratively replace double spaces with single space
            while '  ' in key:
                key = key.replace('  ', ' ')
            # Normalize whitespace, lowercase, strip
            key = ' '.join(key.split()).lower().strip()
            keys.append(key)
    return keys


def load_lyrics_file(filepath):
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


def match_key_to_canonical(key, alias_map):
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
