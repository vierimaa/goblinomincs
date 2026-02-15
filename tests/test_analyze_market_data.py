"""Tests for market analysis functions."""

import pandas as pd

from goblinomincs.analyze_market_data import (
    analyze_buy_sell_now,
    analyze_daily_patterns,
)


def create_sample_item_data():
    """Create sample market data for testing."""
    dates = pd.date_range(start="2025-10-01", end="2025-10-30", freq="6h")
    data = {
        "avg_price": [10.0 + i * 0.1 for i in range(len(dates))],
        "bid": [9.0 + i * 0.1 for i in range(len(dates))],
        "min_buy": [9.5 + i * 0.1 for i in range(len(dates))],
        "available": [50] * len(dates),
    }
    return pd.DataFrame(data, index=dates)


def test_analyze_daily_patterns():
    """Test daily pattern analysis."""
    df = create_sample_item_data()
    result = analyze_daily_patterns(df)

    # Check that all expected keys are present
    expected_keys = [
        "best_buy_day",
        "best_buy_price",
        "best_sell_day",
        "best_sell_price",
        "potential_profit",
    ]
    for key in expected_keys:
        assert key in result

    # Check that buy price is less than or equal to sell price
    assert result["best_buy_price"] <= result["best_sell_price"]

    # Check that day names are valid
    valid_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "N/A",
    ]
    assert result["best_buy_day"] in valid_days
    assert result["best_sell_day"] in valid_days


def test_analyze_buy_sell_now():
    """Test buy/sell now opportunity analysis."""
    # Create sample data with item_name column - need 4 days of hourly data
    dates = pd.date_range(start="2025-10-27", periods=21, freq="6h")
    data = {
        "avg_price": [10.0] * 20 + [8.0],  # Price drops at the end
        "item_name": ["Test Item"] * 21,
    }
    df = pd.DataFrame(data, index=dates)

    result = analyze_buy_sell_now(df, "Test Item")

    # Check that result is not empty
    assert result != {}

    # Check that all expected keys are present
    expected_keys = [
        "item_name",
        "current_price",
        "avg_3d",
        "pct_diff",
        "price_diff",
        "last_updated",
    ]
    for key in expected_keys:
        assert key in result

    # Check that item name matches
    assert result["item_name"] == "Test Item"

    # Check that percentage difference is calculated
    assert isinstance(result["pct_diff"], (int, float))

    # Check that price difference is calculated correctly
    expected_diff = result["current_price"] - result["avg_3d"]
    assert (
        abs(result["price_diff"] - expected_diff) < 0.01
    )  # Allow small floating point difference


def test_analyze_buy_sell_now_empty_data():
    """Test buy/sell now with empty data."""
    # Create empty DataFrame with the required columns
    df = pd.DataFrame(columns=["item_name", "avg_price"])
    result = analyze_buy_sell_now(df, "Nonexistent Item")

    # Should return empty dict for missing item
    assert result == {}
