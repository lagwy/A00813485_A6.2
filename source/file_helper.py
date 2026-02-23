"""
JSON file I/O utilities.

Shared helpers for reading JSON files with consistent error handling.
"""

import json
import os


def load_json_file(filepath, error_label="file"):
    """
    Load JSON from a file.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except json.JSONDecodeError as exc:
        print(f"Error reading {error_label} '{filepath}': {exc}")
        return []
