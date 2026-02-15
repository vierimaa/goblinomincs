"""Tests for data loader utilities."""

import json
from pathlib import Path

import pytest

from goblinomincs.data_loaders import load_json_data


@pytest.mark.integration
def test_load_json_data_with_key():
    """Test loading JSON with key extraction."""
    result = load_json_data(Path("data/items.json"), key="items")

    assert isinstance(result, dict)
    assert len(result) > 0
    # Check it's the items dict, not the full structure
    for item_id, item_name in result.items():
        assert isinstance(item_id, str)
        assert isinstance(item_name, str)


@pytest.mark.integration
def test_load_json_data_without_key():
    """Test loading JSON without key extraction."""
    result = load_json_data(Path("data/items.json"))

    assert isinstance(result, dict)
    # Should have the top-level structure with "items" key
    assert "items" in result
    assert isinstance(result["items"], dict)


@pytest.mark.integration
def test_load_json_data_recipes():
    """Test loading recipes with key extraction."""
    result = load_json_data(Path("data/recipes.json"), key="recipes")

    assert isinstance(result, list)
    assert len(result) > 0
    # Check it's a list of recipe dicts
    assert isinstance(result[0], dict)
    assert "id" in result[0]
    assert "name" in result[0]


@pytest.mark.unit
def test_load_json_data_file_not_found():
    """Test that FileNotFoundError is raised for missing files."""
    with pytest.raises(FileNotFoundError):
        load_json_data(Path("data/nonexistent.json"))


@pytest.mark.unit
def test_load_json_data_invalid_key():
    """Test that KeyError is raised for invalid key."""
    with pytest.raises(KeyError):
        load_json_data(Path("data/items.json"), key="nonexistent_key")


@pytest.mark.unit
def test_load_json_data_invalid_json(tmp_path):
    """Test that JSONDecodeError is raised for invalid JSON."""
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{ invalid json }")

    with pytest.raises(json.JSONDecodeError):
        load_json_data(bad_json)
