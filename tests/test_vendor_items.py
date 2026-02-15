"""Tests for vendor items functionality."""

import pytest

from goblinomincs.vendor_items import get_vendor_price, load_vendor_items


@pytest.mark.integration
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


@pytest.mark.integration
def test_load_vendor_items_with_custom_path(vendor_items_file):
    """Test that vendor_items.json loads with custom path parameter."""
    vendor_items = load_vendor_items(vendor_file=vendor_items_file)

    assert isinstance(vendor_items, dict)
    assert len(vendor_items) > 0


@pytest.mark.unit
@pytest.mark.parametrize(
    "item_id,expected_price,item_name",
    [
        ("3371", 0.2, "Crystal Vial"),
        ("3372", 0.04, "Leaded Vial"),
    ],
)
def test_get_vendor_price(item_id, expected_price, item_name):
    """Test vendor prices for various items."""
    price = get_vendor_price(item_id)
    assert price is not None
    assert price == expected_price


@pytest.mark.unit
def test_get_vendor_price_non_vendor_item():
    """Test that non-vendor items return None."""
    # Arcane Crystal (12363) is not a vendor item
    price = get_vendor_price("12363")
    assert price is None


# File existence is implicitly tested by test_load_vendor_items
