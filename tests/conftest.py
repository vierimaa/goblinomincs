"""Shared test fixtures for goblinomincs test suite."""

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing.

    Returns a DataFrame with 30 days of data for various items
    commonly used in crafting calculations and market analysis tests.
    """
    dates = pd.date_range(start="2025-10-01", periods=30, freq="D")

    items_data = {
        "Gromsblood": 0.5,
        "Mountain Silversage": 0.8,
        "Swiftness Potion": 2.0,
        "Swiftthistle": 0.3,
        "Briarthorn": 0.1,
        "Golden Sansam": 0.6,
        "Plaguebloom": 0.4,
        "Stonescale Oil": 0.7,
        "Dreamfoil": 0.5,
        "Icecap": 0.6,
        "Potion of Quickness": 3.5,
        "Greater Fire Protection Potion": 2.5,
    }

    data_frames = []
    for item_name, base_price in items_data.items():
        data = {
            "item_name": [item_name] * len(dates),
            "avg_price": [base_price + (i * 0.01) for i in range(len(dates))],
            "bid": [(base_price - 0.1) + (i * 0.01) for i in range(len(dates))],
            "min_buy": [(base_price - 0.05) + (i * 0.01) for i in range(len(dates))],
            "available": [50] * len(dates),
        }
        df = pd.DataFrame(data, index=dates)
        data_frames.append(df)

    return pd.concat(data_frames)


@pytest.fixture
def sample_item_data():
    """Create sample market data for a single item.

    Returns a DataFrame with 30 days of hourly (6h intervals) data
    suitable for testing time-series analysis and pattern detection.
    """
    dates = pd.date_range(start="2025-10-01", end="2025-10-30", freq="6h")
    data = {
        "avg_price": [10.0 + i * 0.1 for i in range(len(dates))],
        "bid": [9.0 + i * 0.1 for i in range(len(dates))],
        "min_buy": [9.5 + i * 0.1 for i in range(len(dates))],
        "available": [50] * len(dates),
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def test_data_dir():
    """Return path to test data directory."""
    return Path("data")


@pytest.fixture
def items_file(test_data_dir):
    """Return path to items.json."""
    return test_data_dir / "items.json"


@pytest.fixture
def recipes_file(test_data_dir):
    """Return path to recipes.json."""
    return test_data_dir / "recipes.json"


@pytest.fixture
def vendor_items_file(test_data_dir):
    """Return path to vendor_items.json."""
    return test_data_dir / "vendor_items.json"
