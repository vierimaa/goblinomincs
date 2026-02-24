"""Tests for pure market analysis computation functions."""

import pandas as pd
import pytest

from goblinomincs.market_analysis import (
    analyze_buy_sell_now,
    analyze_daily_patterns,
    get_buy_sell_opportunities,
    get_recipes_by_source,
)


@pytest.mark.unit
def test_analyze_daily_patterns(sample_item_data):
    """Test daily pattern analysis."""
    df = sample_item_data
    result = analyze_daily_patterns(df)

    expected_keys = [
        "best_buy_day",
        "best_buy_price",
        "best_sell_day",
        "best_sell_price",
        "potential_profit",
    ]
    for key in expected_keys:
        assert key in result

    assert result["best_buy_price"] <= result["best_sell_price"]

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


@pytest.mark.unit
def test_analyze_buy_sell_now():
    """Test buy/sell now opportunity analysis."""
    dates = pd.date_range(start="2025-10-27", periods=21, freq="6h")
    data = {
        "avg_price": [10.0] * 20 + [8.0],  # Price drops at the end
        "item_name": ["Test Item"] * 21,
    }
    df = pd.DataFrame(data, index=dates)

    result = analyze_buy_sell_now(df, "Test Item")

    assert result != {}

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

    assert result["item_name"] == "Test Item"
    assert isinstance(result["pct_diff"], (int, float))

    expected_diff = result["current_price"] - result["avg_3d"]
    assert abs(result["price_diff"] - expected_diff) < 0.01


@pytest.mark.unit
def test_analyze_buy_sell_now_empty_data():
    """Test buy/sell now with empty data."""
    df = pd.DataFrame(columns=["item_name", "avg_price"])
    result = analyze_buy_sell_now(df, "Nonexistent Item")

    assert result == {}


@pytest.mark.unit
def test_get_buy_sell_opportunities():
    """Test getting buy and sell opportunities."""
    dates = pd.date_range(start="2025-10-27", periods=21, freq="6h")

    item1_data = pd.DataFrame(
        {"avg_price": [10.0] * 20 + [8.0], "item_name": ["Cheap Item"] * 21},
        index=dates,
    )
    item2_data = pd.DataFrame(
        {"avg_price": [10.0] * 20 + [12.0], "item_name": ["Expensive Item"] * 21},
        index=dates,
    )
    item3_data = pd.DataFrame(
        {"avg_price": [10.0] * 21, "item_name": ["Stable Item"] * 21},
        index=dates,
    )

    df = pd.concat([item1_data, item2_data, item3_data])
    items = {"1": "Cheap Item", "2": "Expensive Item", "3": "Stable Item"}

    buy_opps, sell_opps = get_buy_sell_opportunities(df, items, threshold_pct=5.0)

    assert isinstance(buy_opps, list)
    assert isinstance(sell_opps, list)

    buy_names = [opp["item_name"] for opp in buy_opps]
    assert "Cheap Item" in buy_names

    sell_names = [opp["item_name"] for opp in sell_opps]
    assert "Expensive Item" in sell_names

    if len(buy_opps) > 1:
        for i in range(len(buy_opps) - 1):
            assert abs(buy_opps[i]["price_diff"]) >= abs(buy_opps[i + 1]["price_diff"])

    if len(sell_opps) > 1:
        for i in range(len(sell_opps) - 1):
            assert sell_opps[i]["price_diff"] >= sell_opps[i + 1]["price_diff"]


@pytest.mark.unit
def test_get_buy_sell_opportunities_custom_threshold():
    """Test that threshold parameter filters opportunities correctly."""
    dates = pd.date_range(start="2025-10-27", periods=21, freq="6h")

    item_data = pd.DataFrame(
        {"avg_price": [10.0] * 20 + [9.7], "item_name": ["Small Change"] * 21},
        index=dates,
    )

    df = item_data
    items = {"1": "Small Change"}

    buy_opps_5, sell_opps_5 = get_buy_sell_opportunities(df, items, threshold_pct=5.0)
    assert len(buy_opps_5) == 0
    assert len(sell_opps_5) == 0

    buy_opps_2, sell_opps_2 = get_buy_sell_opportunities(df, items, threshold_pct=2.0)
    assert len(buy_opps_2) == 1
    assert buy_opps_2[0]["item_name"] == "Small Change"


@pytest.mark.unit
def test_get_recipes_by_source(sample_market_data):
    """Test grouping recipes by source with cost analysis."""
    df = sample_market_data

    result = get_recipes_by_source(df)

    assert isinstance(result, dict)
    assert len(result) > 0

    assert "Alchemy" in result

    for _source, recipes in result.items():
        assert isinstance(recipes, list)
        assert len(recipes) > 0

        for recipe in recipes:
            assert "recipe_name" in recipe
            assert "total_cost" in recipe
            assert "current_price" in recipe or recipe["current_price"] is None

        recipe_names = [r["recipe_name"] for r in recipes]
        assert recipe_names == sorted(recipe_names)
