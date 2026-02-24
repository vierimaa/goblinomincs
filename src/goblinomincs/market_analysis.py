"""Pure market data computation — no display logic.

All functions return plain data structures (dicts, lists) suitable for
further processing or presentation by display.py.
"""

import pandas as pd

from goblinomincs.recipe_analysis import (
    calculate_crafting_cost,
    load_recipes,
)


def analyze_daily_patterns(item_df: pd.DataFrame) -> dict:
    """Analyze which days are best for buying/selling an item.

    Args:
        item_df: DataFrame with item price data, must have 'avg_price' column
                 and datetime index

    Returns:
        dict with best buy/sell days, prices, and potential profit percentage
    """
    daily_prices = (
        item_df.groupby(item_df.index.day_name())["avg_price"]
        .agg(["mean", "count"])
        .round(2)
    )

    valid_days = daily_prices[daily_prices["count"] >= 3]

    if valid_days.empty:
        return {
            "best_buy_day": "N/A",
            "best_buy_price": 0,
            "best_sell_day": "N/A",
            "best_sell_price": 0,
            "potential_profit": 0,
        }

    best_buy_day = valid_days.sort_values("mean").index[0]
    best_sell_day = valid_days.sort_values("mean", ascending=False).index[0]

    best_buy_price = valid_days.loc[best_buy_day, "mean"]
    best_sell_price = valid_days.loc[best_sell_day, "mean"]
    potential_profit = ((best_sell_price - best_buy_price) / best_buy_price) * 100

    return {
        "best_buy_day": best_buy_day,
        "best_buy_price": best_buy_price,
        "best_sell_day": best_sell_day,
        "best_sell_price": best_sell_price,
        "potential_profit": potential_profit,
    }


def analyze_buy_sell_now(df: pd.DataFrame, item_name: str) -> dict:
    """Analyze if an item is a good buy or sell opportunity right now.

    Compares the latest price to the 3-day average to identify opportunities.

    Args:
        df: DataFrame with all market data
        item_name: Name of the item to analyze

    Returns:
        dict with current price, 3-day average, and percentage difference,
        or empty dict if the item has no data or insufficient history
    """
    item_df = df.loc[df["item_name"] == item_name].copy()

    if item_df.empty:
        return {}

    latest_price = item_df.iloc[-1]["avg_price"]
    latest_time = item_df.index[-1]

    three_days_ago = latest_time - pd.Timedelta(days=3)
    three_day_data = item_df.loc[
        (item_df.index >= three_days_ago) & (item_df.index < latest_time)
    ]

    if three_day_data.empty:
        return {}

    avg_3d = three_day_data["avg_price"].mean()
    pct_diff = ((latest_price - avg_3d) / avg_3d) * 100

    return {
        "item_name": item_name,
        "current_price": latest_price,
        "avg_3d": avg_3d,
        "pct_diff": pct_diff,
        "price_diff": latest_price - avg_3d,
        "last_updated": latest_time,
    }


def analyze_item(df: pd.DataFrame, item_name: str) -> dict:
    """Analyze market data for a specific item and calculate summary statistics.

    Args:
        df: DataFrame with all market data
        item_name: Name of the item to analyze

    Returns:
        dict with analysis results including averages, trends and best trading days,
        or empty dict if no data is found for the item
    """
    item_df = df.loc[df["item_name"] == item_name].copy()

    if item_df.empty:
        return {}

    avg_30d = item_df["avg_price"].mean()
    latest_price = item_df.iloc[-1]["avg_price"]

    cutoff_date = item_df.index.max() - pd.Timedelta(days=7)
    avg_7d = item_df.loc[item_df.index >= cutoff_date, "avg_price"].mean()

    trend = ((avg_7d - avg_30d) / avg_30d * 100) if avg_7d and avg_30d else 0

    daily_patterns = analyze_daily_patterns(item_df)

    return {
        "item_name": item_name,
        "latest_price": latest_price,
        "avg_30d": avg_30d,
        "avg_7d": avg_7d,
        "trend": trend,
        "best_buy_day": daily_patterns["best_buy_day"],
        "best_buy_price": daily_patterns["best_buy_price"],
        "best_sell_day": daily_patterns["best_sell_day"],
        "best_sell_price": daily_patterns["best_sell_price"],
        "flip_profit": daily_patterns["potential_profit"],
    }


def get_buy_sell_opportunities(
    df: pd.DataFrame, items: dict, threshold_pct: float = 5
) -> tuple[list[dict], list[dict]]:
    """Calculate buy and sell opportunities based on price vs 3-day average.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to item names
        threshold_pct: Minimum percentage difference to trigger opportunity (default: 5%)

    Returns:
        tuple: (buy_opportunities, sell_opportunities) sorted by gold difference
    """
    buy_opportunities = []
    sell_opportunities = []

    for _item_id, item_name in items.items():
        analysis = analyze_buy_sell_now(df, item_name)
        if not analysis:
            continue

        if analysis["pct_diff"] < -threshold_pct:
            buy_opportunities.append(analysis)
        elif analysis["pct_diff"] > threshold_pct:
            sell_opportunities.append(analysis)

    buy_opportunities.sort(key=lambda x: abs(x["price_diff"]), reverse=True)
    sell_opportunities.sort(key=lambda x: x["price_diff"], reverse=True)

    return buy_opportunities, sell_opportunities


def get_recipes_by_source(df: pd.DataFrame) -> dict[str, list[dict]]:
    """Group recipes by source (profession) with cost analysis.

    Args:
        df: DataFrame with all market data

    Returns:
        dict: Dictionary mapping source names to lists of recipe analysis dicts,
              each list sorted by recipe name
    """
    recipes = load_recipes()
    recipes_by_source: dict[str, list[dict]] = {}

    for recipe in recipes:
        source = recipe.get("source", "Unknown")
        if source not in recipes_by_source:
            recipes_by_source[source] = []

        analysis = calculate_crafting_cost(recipe, df)
        recipes_by_source[source].append(analysis)

    for source in recipes_by_source:
        recipes_by_source[source].sort(key=lambda r: r["recipe_name"])

    return recipes_by_source
