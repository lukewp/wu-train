
import os

def load_lyrics_file(filepath):
    """
    Load and return the full contents of the lyrics file as a string.
    Raises FileNotFoundError or UnicodeDecodeError as appropriate.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
