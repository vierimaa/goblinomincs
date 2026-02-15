"""Recipe and crafting cost analysis utilities."""

from pathlib import Path

import pandas as pd

from goblinomincs.data_loaders import load_json_data
from goblinomincs.vendor_items import get_vendor_price

RECIPES_FILE = Path("data/recipes.json")


def load_recipes(recipes_file: Path | None = None) -> list:
    """Load all recipes from recipes.json.

    Args:
        recipes_file: Optional path to recipes.json file (uses default if None)

    Returns:
        list: List of recipe dictionaries
    """
    file_path = recipes_file or RECIPES_FILE
    return load_json_data(file_path, key="recipes")


def build_recipe_lookup() -> dict:
    """Build a lookup dictionary mapping item IDs to their recipes.

    Returns:
        dict: Dictionary mapping item ID (str) to recipe dict
    """
    all_recipes = load_recipes()
    lookup = {}
    for recipe_data in all_recipes:
        item_id = str(recipe_data["id"])
        lookup[item_id] = recipe_data
    return lookup


def _get_market_price_for_reagent(
    reagent_name: str, df: pd.DataFrame
) -> tuple[float | None, float | None]:
    """Get current and 7-day average market price for a reagent.

    Args:
        reagent_name: Name of the reagent
        df: DataFrame with current market data

    Returns:
        tuple: (current_price, 7d_avg_price) or (None, None) if not found
    """
    reagent_data = df[df["item_name"] == reagent_name]
    if reagent_data.empty:
        return None, None

    current_price = reagent_data.iloc[-1]["avg_price"]
    cutoff_date = reagent_data.index.max() - pd.Timedelta(days=7)
    reagent_7d = reagent_data.loc[reagent_data.index >= cutoff_date]
    price_7d = reagent_7d["avg_price"].mean() if not reagent_7d.empty else current_price
    return current_price, price_7d


def _get_craft_price_for_reagent(
    reagent_id: str, df: pd.DataFrame, recipe_lookup: dict, cost_cache: dict
) -> tuple[float | None, float | None]:
    """Calculate the cost to craft a reagent if recipe exists.

    Args:
        reagent_id: Item ID of the reagent
        df: DataFrame with current market data
        recipe_lookup: Dictionary mapping item IDs to recipes
        cost_cache: Cache for reagent costs

    Returns:
        tuple: (craft_cost, craft_cost_7d) or (None, None) if not craftable
    """
    if reagent_id not in recipe_lookup:
        return None, None

    try:
        craft_analysis = _calculate_crafting_cost_internal(
            recipe_lookup[reagent_id], df, recipe_lookup, cost_cache
        )
        if craft_analysis["missing_prices"]:
            return None, None
        return craft_analysis["total_cost"], craft_analysis["total_cost_7d"]
    except RecursionError:
        # Prevent infinite loops from circular dependencies
        return None, None


def _choose_best_price(
    craft_price: float | None,
    craft_price_7d: float | None,
    market_price: float | None,
    market_price_7d: float | None,
) -> tuple[float | None, float | None, str]:
    """Choose the cheapest option between crafting and buying.

    Args:
        craft_price: Current cost to craft
        craft_price_7d: 7-day average cost to craft
        market_price: Current market price
        market_price_7d: 7-day average market price

    Returns:
        tuple: (best_price, best_price_7d, source) where source is 'crafted' or 'auction'
               Returns (None, None, 'missing') if neither option available
    """
    options = []
    if craft_price is not None:
        options.append((craft_price, craft_price_7d, "crafted"))
    if market_price is not None:
        options.append((market_price, market_price_7d, "auction"))

    if not options:
        return None, None, "missing"

    return min(options, key=lambda x: x[0])


def get_best_reagent_price(
    reagent_id: str,
    reagent_name: str,
    df: pd.DataFrame,
    recipe_lookup: dict,
    cost_cache: dict,
) -> tuple[float | None, float | None, str]:
    """Get the best price for a reagent (vendor, craft, or market).

    Args:
        reagent_id: Item ID of the reagent
        reagent_name: Name of the reagent
        df: DataFrame with current market data
        recipe_lookup: Dictionary mapping item IDs to recipes
        cost_cache: Cache to avoid recalculating costs

    Returns:
        tuple: (current_price, 7d_avg_price, source)
               source can be 'vendor', 'crafted', or 'auction'
    """
    # Check cache first to avoid redundant calculations
    if reagent_id in cost_cache:
        cached = cost_cache[reagent_id]
        return cached["unit_price"], cached["unit_price_7d"], cached["source"]

    # Vendor price always wins if available
    vendor_price = get_vendor_price(reagent_id)
    if vendor_price is not None:
        cost_cache[reagent_id] = {
            "unit_price": vendor_price,
            "unit_price_7d": vendor_price,
            "source": "vendor",
        }
        return vendor_price, vendor_price, "vendor"

    # Compare craft vs market prices
    craft_price, craft_price_7d = _get_craft_price_for_reagent(
        reagent_id, df, recipe_lookup, cost_cache
    )
    market_price, market_price_7d = _get_market_price_for_reagent(reagent_name, df)

    best_price, best_price_7d, source = _choose_best_price(
        craft_price, craft_price_7d, market_price, market_price_7d
    )

    # Cache the result
    if best_price is not None:
        cost_cache[reagent_id] = {
            "unit_price": best_price,
            "unit_price_7d": best_price_7d,
            "source": source,
        }

    return best_price, best_price_7d, source


def _calculate_crafting_cost_internal(
    recipe: dict, df: pd.DataFrame, recipe_lookup: dict, cost_cache: dict
) -> dict:
    """Internal function to calculate crafting cost with recursion support.

    Args:
        recipe: Recipe dictionary with reagents list
        df: DataFrame with current market data
        recipe_lookup: Dictionary mapping item IDs to recipes
        cost_cache: Cache for reagent costs

    Returns:
        dict with crafting cost breakdown
    """
    total_cost = 0.0
    total_cost_7d = 0.0
    reagent_costs = []
    missing_prices = []

    for reagent in recipe["reagents"]:
        reagent_id = str(reagent["id"])
        reagent_name = reagent["name"]
        quantity = reagent["quantity"]

        unit_price, unit_price_7d, source = get_best_reagent_price(
            reagent_id, reagent_name, df, recipe_lookup, cost_cache
        )

        if unit_price is None:
            missing_prices.append(reagent_name)
            continue

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


def calculate_crafting_cost(recipe: dict, df: pd.DataFrame) -> dict:
    """Calculate the cost to craft a recipe based on current market prices.

    This function supports recursive costing - if a reagent is itself craftable,
    it will compare the cost of buying vs crafting and use the cheaper option.

    Args:
        recipe: Recipe dictionary with reagents list
        df: DataFrame with current market data

    Returns:
        dict with crafting cost breakdown and profit analysis
    """
    recipe_lookup = build_recipe_lookup()
    cost_cache = {}  # Cache to avoid recalculating costs
    return _calculate_crafting_cost_internal(recipe, df, recipe_lookup, cost_cache)


def get_profitable_recipes(df: pd.DataFrame, min_profit_pct: float = 0) -> list:
    """Get all recipes sorted by profitability.

    Args:
        df: DataFrame with current market data
        min_profit_pct: Minimum profit percentage to include

    Returns:
        list: List of recipe analysis dictionaries sorted by profit
    """
    recipes = load_recipes()
    recipe_lookup = build_recipe_lookup()
    cost_cache = {}  # Shared cache for all recipes
    profitable = []

    for recipe in recipes:
        analysis = _calculate_crafting_cost_internal(
            recipe, df, recipe_lookup, cost_cache
        )

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
