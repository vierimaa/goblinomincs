"""Utilities for handling vendor items with fixed prices."""

from pathlib import Path

from goblinomincs.data_loaders import load_json_data

VENDOR_ITEMS_FILE = Path("data/vendor_items.json")


def load_vendor_items(vendor_file: Path | None = None) -> dict:
    """Load vendor items with fixed prices from vendor_items.json.

    Args:
        vendor_file: Optional path to vendor_items.json file (uses default if None)

    Returns:
        dict: Dictionary mapping item IDs to vendor item data
    """
    file_path = vendor_file or VENDOR_ITEMS_FILE
    return load_json_data(file_path, key="vendor_items")


def get_vendor_price(item_id: str) -> float | None:
    """Get the vendor price for an item if it's a vendor item.

    Args:
        item_id: The item ID to check

    Returns:
        float: The vendor price in gold, or None if not a vendor item
    """
    vendor_items = load_vendor_items()
    if item_id in vendor_items:
        return vendor_items[item_id]["vendor_price"]
    return None
