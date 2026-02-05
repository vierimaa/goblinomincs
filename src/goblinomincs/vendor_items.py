"""Utilities for handling vendor items with fixed prices."""

import json
from pathlib import Path
from typing import Optional

VENDOR_ITEMS_FILE = Path("data/vendor_items.json")


def load_vendor_items() -> dict:
    """Load vendor items with fixed prices from vendor_items.json.

    Returns:
        dict: Dictionary mapping item IDs to vendor item data
    """
    with open(VENDOR_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["vendor_items"]


def get_vendor_price(item_id: str) -> Optional[float]:
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
