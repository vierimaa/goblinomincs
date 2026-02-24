"""Tests for the auction data fetcher, including regression tests for the
items.json nested-schema bug where item values were mistakenly treated as
plain strings instead of {name, category} objects.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from goblinomincs.fetcher import main, should_fetch_item


@pytest.mark.unit
def test_main_reads_nested_item_schema(tmp_path):
    """Regression test: main() must extract item name from nested item objects.

    Before the fix, items.json was read as {id: name_string}, but it now stores
    {id: {"name": ..., "category": ...}}. Passing the dict directly as item_name
    caused crashes downstream (e.g. should_fetch_item building a path with a dict).

    This test verifies that main() correctly extracts item_info["name"] and passes
    a plain string to fetch_and_save_item.
    """
    items_data = {
        "items": {
            "12363": {"name": "Arcane Crystal", "category": "Materials"},
            "10620": {"name": "Thorium Ore", "category": "Materials"},
        }
    }
    items_file = tmp_path / "items.json"
    items_file.write_text(json.dumps(items_data))

    captured_item_names: list = []

    def fake_fetch_and_save(item_id, item_name, realm, console_inst=None):
        captured_item_names.append(item_name)
        return True

    with (
        patch("goblinomincs.fetcher.should_fetch_item", return_value=True),
        patch("goblinomincs.fetcher.fetch_and_save_item", side_effect=fake_fetch_and_save),
    ):
        main(items_file=items_file)

    # All captured names must be plain strings, not dicts
    assert len(captured_item_names) == 2
    for name in captured_item_names:
        assert isinstance(name, str), (
            f"item_name should be a str, got {type(name).__name__!r}: {name!r}. "
            "Check that main() reads item_info['name'] from the nested schema."
        )

    assert set(captured_item_names) == {"Arcane Crystal", "Thorium Ore"}


@pytest.mark.unit
def test_main_skips_recent_items(tmp_path):
    """Items with recent data should be skipped and not passed to fetch_and_save_item."""
    items_data = {
        "items": {
            "12363": {"name": "Arcane Crystal", "category": "Materials"},
        }
    }
    items_file = tmp_path / "items.json"
    items_file.write_text(json.dumps(items_data))

    mock_fetch = MagicMock(return_value=True)

    with (
        patch("goblinomincs.fetcher.should_fetch_item", return_value=False),
        patch("goblinomincs.fetcher.fetch_and_save_item", mock_fetch),
    ):
        main(items_file=items_file)

    mock_fetch.assert_not_called()


@pytest.mark.unit
def test_should_fetch_item_missing_file(tmp_path):
    """should_fetch_item returns True when the CSV file does not exist."""
    # Point to a realm directory that has no files
    with patch("goblinomincs.fetcher.is_recent", return_value=False):
        result = should_fetch_item("12363", "Arcane Crystal", realm="ambershire")

    assert result is True


@pytest.mark.unit
def test_should_fetch_item_recent_file():
    """should_fetch_item returns False when the CSV file is recent."""
    with patch("goblinomincs.fetcher.is_recent", return_value=True):
        result = should_fetch_item("12363", "Arcane Crystal", realm="ambershire")

    assert result is False
