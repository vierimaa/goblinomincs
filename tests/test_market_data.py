"""Tests for market data loading functions."""

from pathlib import Path

import pytest

from goblinomincs.market_data import load_items


@pytest.mark.integration
def test_load_items():
    """Test that items.json loads the raw items mapping correctly."""
    items_map = load_items()

    assert isinstance(items_map, dict)
    assert len(items_map) > 0

    for item_id, item_info in items_map.items():
        assert isinstance(item_id, str)
        assert isinstance(item_info, dict)
        assert "name" in item_info and isinstance(item_info["name"], str)
        assert "category" in item_info and isinstance(item_info["category"], str)


@pytest.mark.integration
def test_load_items_with_custom_path(items_file):
    """Test that items.json loads with custom path parameter."""
    items_map = load_items(items_file=items_file)

    assert isinstance(items_map, dict)
    assert len(items_map) > 0


@pytest.mark.integration
def test_market_data_directory_exists():
    """Test that market data directory exists."""
    data_dir = Path("data/market_data/ambershire")
    assert data_dir.exists(), "Market data directory not found"
    assert data_dir.is_dir(), "Market data path is not a directory"


@pytest.mark.integration
@pytest.mark.integration
def test_item_categories_present():
    """Verify categories exist for items in the mapping."""
    items_map = load_items()
    for item_id, item_info in items_map.items():
        assert "category" in item_info and isinstance(item_info["category"], str)


@pytest.mark.integration
def test_item_categories_with_custom_path(items_file):
    items_map = load_items(items_file=items_file)
    assert isinstance(items_map, dict)
    assert len(items_map) > 0

