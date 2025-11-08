"""Tests for vendor items functionality."""

import pytest
from pathlib import Path
from vendor_items import load_vendor_items, get_vendor_price


def test_load_vendor_items():
    """Test that vendor_items.json loads correctly."""
    vendor_items = load_vendor_items()

    # Check that it returns a dictionary
    assert isinstance(vendor_items, dict)

    # Check structure of vendor items
    for item_id, item_data in vendor_items.items():
        assert isinstance(item_id, str)
        assert isinstance(item_data, dict)
        assert "name" in item_data
        assert "vendor_price" in item_data
        assert isinstance(item_data["vendor_price"], (int, float))
        assert item_data["vendor_price"] > 0


def test_get_vendor_price_crystal_vial():
    """Test that Crystal Vial returns correct vendor price."""
    # Crystal Vial (item ID 3371) should be 0.2g
    price = get_vendor_price("3371")
    assert price is not None
    assert price == 0.2


def test_get_vendor_price_non_vendor_item():
    """Test that non-vendor items return None."""
    # Arcane Crystal (12363) is not a vendor item
    price = get_vendor_price("12363")
    assert price is None


def test_vendor_items_json_exists():
    """Test that vendor_items.json file exists."""
    vendor_file = Path("data/vendor_items.json")
    assert vendor_file.exists(), "data/vendor_items.json file not found"
