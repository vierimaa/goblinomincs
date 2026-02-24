"""Generic JSON file loading utilities."""

import json
from pathlib import Path


def load_json_data(file_path: Path, key: str | None = None) -> dict | list:
    """Load JSON data from a file with optional key extraction.

    Args:
        file_path: Path to the JSON file
        key: Optional key to extract from the loaded JSON (default: None)

    Returns:
        dict | list: The loaded JSON data, or extracted value if key is provided

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        KeyError: If the specified key doesn't exist in the JSON
    """
    with file_path.open(encoding="utf-8") as file_obj:
        json_data = json.load(file_obj)

    if not key:
        return json_data

    return json_data[key]
