"""Tests for vendor items functionality."""

from goblinomincs.vendor_items import get_vendor_price, load_vendor_items


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


def test_get_vendor_price_leaded_vial():
    """Test that Leaded Vial returns correct vendor price."""
    # Leaded Vial (item ID 3372) should be 0.04g
    price = get_vendor_price("3372")
    assert price is not None
    assert price == 0.04


def test_get_vendor_price_non_vendor_item():
    """Test that non-vendor items return None."""
    # Arcane Crystal (12363) is not a vendor item
    price = get_vendor_price("12363")
    assert price is None


# File existence is implicitly tested by test_load_vendor_items
