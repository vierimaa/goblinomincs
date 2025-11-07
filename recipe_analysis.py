"""Recipe and crafting cost analysis utilities."""

import json
from pathlib import Path
from typing import Optional
import pandas as pd
from vendor_items import get_vendor_price

RECIPES_FILE = Path("data/recipes.json")


def load_recipes() -> list:
    """Load all recipes from recipes.json.

    Returns:
        list: List of recipe dictionaries
    """
    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["recipes"]


def calculate_crafting_cost(recipe: dict, df: pd.DataFrame) -> dict:
    """Calculate the cost to craft a recipe based on current market prices.

    Args:
        recipe: Recipe dictionary with reagents list
        df: DataFrame with current market data

    Returns:
        dict with crafting cost breakdown and profit analysis
    """
    total_cost = 0.0
    total_cost_7d = 0.0
    reagent_costs = []
    missing_prices = []

    for reagent in recipe["reagents"]:
        reagent_id = str(reagent["id"])
        reagent_name = reagent["name"]
        quantity = reagent["quantity"]

        # Check if it's a vendor item first
        vendor_price = get_vendor_price(reagent_id)
        if vendor_price is not None:
            unit_price = vendor_price
            unit_price_7d = vendor_price  # Vendor prices don't change
            source = "vendor"
        else:
            # Get current market price
            reagent_data = df[df["item_name"] == reagent_name]
            if reagent_data.empty:
                missing_prices.append(reagent_name)
                continue

            # Use the most recent price
            unit_price = reagent_data.iloc[-1]["avg_price"]

            # Calculate 7-day average
            cutoff_date = reagent_data.index.max() - pd.Timedelta(days=7)
            reagent_7d = reagent_data.loc[reagent_data.index >= cutoff_date]
            unit_price_7d = (
                reagent_7d["avg_price"].mean() if not reagent_7d.empty else unit_price
            )

            source = "auction"

        reagent_cost = unit_price * quantity
        reagent_cost_7d = unit_price_7d * quantity
        total_cost += reagent_cost
        total_cost_7d += reagent_cost_7d

        reagent_costs.append(
            {
                "name": reagent_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "unit_price_7d": unit_price_7d,
                "total_cost": reagent_cost,
                "source": source,
            }
        )

    # Get the crafted item's current market price
    crafted_item_name = recipe["name"]
    crafted_data = df[df["item_name"] == crafted_item_name]

    if crafted_data.empty:
        current_price = None
        current_price_7d = None
        profit = None
        profit_pct = None
        profit_7d = None
        profit_7d_pct = None
    else:
        current_price = crafted_data.iloc[-1]["avg_price"]

        # Calculate 7-day average for crafted item
        cutoff_date = crafted_data.index.max() - pd.Timedelta(days=7)
        crafted_7d = crafted_data.loc[crafted_data.index >= cutoff_date]
        current_price_7d = (
            crafted_7d["avg_price"].mean() if not crafted_7d.empty else current_price
        )

        profit = current_price - total_cost
        profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

        profit_7d = current_price_7d - total_cost_7d
        profit_7d_pct = (profit_7d / total_cost_7d * 100) if total_cost_7d > 0 else 0

    return {
        "recipe_id": recipe["id"],
        "recipe_name": recipe["name"],
        "source": recipe.get("source", "Unknown"),
        "total_cost": total_cost,
        "total_cost_7d": total_cost_7d,
        "current_price": current_price,
        "current_price_7d": current_price_7d,
        "profit": profit,
        "profit_pct": profit_pct,
        "profit_7d": profit_7d,
        "profit_7d_pct": profit_7d_pct,
        "reagent_costs": reagent_costs,
        "missing_prices": missing_prices,
    }


def get_profitable_recipes(df: pd.DataFrame, min_profit_pct: float = 0) -> list:
    """Get all recipes sorted by profitability.

    Args:
        df: DataFrame with current market data
        min_profit_pct: Minimum profit percentage to include

    Returns:
        list: List of recipe analysis dictionaries sorted by profit
    """
    recipes = load_recipes()
    profitable = []

    for recipe in recipes:
        analysis = calculate_crafting_cost(recipe, df)

        # Only include recipes where we have all prices and meet min profit
        if (
            analysis["profit"] is not None
            and not analysis["missing_prices"]
            and analysis["profit_pct"] >= min_profit_pct
        ):
            profitable.append(analysis)

    # Sort by absolute profit (gold)
    profitable.sort(key=lambda x: x["profit"], reverse=True)
    return profitable
