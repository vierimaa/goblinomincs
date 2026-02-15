"""Tests for market data loading functions."""

from pathlib import Path

from goblinomincs.market_data import load_item_names


def test_load_item_names():
    """Test that items.json loads correctly."""
    items = load_item_names()

    # Check that it returns a dictionary
    assert isinstance(items, dict)

    # Check that it's not empty
    assert len(items) > 0

    # Check that keys are strings (item IDs)
    for item_id in items:
        assert isinstance(item_id, str)

    # Check that values are strings (item names)
    for item_name in items.values():
        assert isinstance(item_name, str)
        assert len(item_name) > 0


def test_market_data_directory_exists():
    """Test that market data directory exists."""
    data_dir = Path("data/market_data/ambershire")
    assert data_dir.exists(), "Market data directory not found"
    assert data_dir.is_dir(), "Market data path is not a directory"
