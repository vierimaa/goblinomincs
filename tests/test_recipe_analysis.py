"""Tests for recipe analysis and crafting cost calculations."""

import pandas as pd
import pytest

from goblinomincs.recipe_analysis import (
    _choose_best_price,
    _get_market_price_for_reagent,
    build_recipe_lookup,
    calculate_crafting_cost,
    get_profitable_recipes,
    load_recipes,
)


@pytest.mark.integration
def test_load_recipes():
    """Test that recipes.json loads correctly."""
    recipes = load_recipes()

    assert isinstance(recipes, list)
    assert len(recipes) > 0

    # Check structure of first recipe
    recipe = recipes[0]
    assert "id" in recipe
    assert "name" in recipe
    assert "source" in recipe
    assert "reagents" in recipe
    assert isinstance(recipe["reagents"], list)

    # Check reagent structure
    if recipe["reagents"]:
        reagent = recipe["reagents"][0]
        assert "id" in reagent
        assert "name" in reagent
        assert "quantity" in reagent


@pytest.mark.integration
def test_load_recipes_with_custom_path(recipes_file):
    """Test that recipes.json loads with custom path parameter."""
    recipes = load_recipes(recipes_file=recipes_file)

    assert isinstance(recipes, list)
    assert len(recipes) > 0


@pytest.mark.unit
def test_build_recipe_lookup():
    """Test recipe lookup dictionary is built correctly."""
    lookup = build_recipe_lookup()

    assert isinstance(lookup, dict)
    assert len(lookup) > 0

    # Check that keys are strings (item IDs)
    for item_id, recipe in lookup.items():
        assert isinstance(item_id, str)
        assert isinstance(recipe, dict)
        assert "id" in recipe
        assert str(recipe["id"]) == item_id


@pytest.mark.unit
def test_swiftness_potion_recipe_exists():
    """Test that Swiftness Potion recipe was added correctly."""
    lookup = build_recipe_lookup()

    # Swiftness Potion should have ID 2459
    assert "2459" in lookup
    recipe = lookup["2459"]
    assert recipe["name"] == "Swiftness Potion"
    assert recipe["source"] == "Alchemy"

    # Check it has the right reagents
    assert len(recipe["reagents"]) == 3
    reagent_ids = {r["id"] for r in recipe["reagents"]}
    assert 2452 in reagent_ids  # Swiftthistle
    assert 2450 in reagent_ids  # Briarthorn
    assert 3372 in reagent_ids  # Leaded Vial


@pytest.mark.unit
def test_potion_of_quickness_uses_swiftness_potion():
    """Test that Potion of Quickness correctly uses Swiftness Potion as reagent."""
    lookup = build_recipe_lookup()

    assert "61181" in lookup
    recipe = lookup["61181"]
    assert recipe["name"] == "Potion of Quickness"

    # Check Swiftness Potion is a reagent
    reagent_ids = {r["id"] for r in recipe["reagents"]}
    assert 2459 in reagent_ids  # Swiftness Potion


@pytest.mark.unit
def test_get_market_price_for_reagent(sample_market_data):
    """Test market price retrieval for reagents."""
    df = sample_market_data

    current, avg_7d = _get_market_price_for_reagent("Gromsblood", df)

    assert current is not None
    assert avg_7d is not None
    assert current > 0
    assert avg_7d > 0


@pytest.mark.unit
def test_get_market_price_missing_item(sample_market_data):
    """Test market price retrieval for non-existent item."""
    df = sample_market_data

    current, avg_7d = _get_market_price_for_reagent("Nonexistent Item", df)

    assert current is None
    assert avg_7d is None


@pytest.mark.unit
def test_choose_best_price_craft_cheaper():
    """Test that crafting is chosen when cheaper than market."""
    best, best_7d, source = _choose_best_price(
        craft_price=1.0, craft_price_7d=1.1, market_price=1.5, market_price_7d=1.6
    )

    assert best == 1.0
    assert best_7d == 1.1
    assert source == "crafted"


@pytest.mark.unit
def test_choose_best_price_market_cheaper():
    """Test that market is chosen when cheaper than crafting."""
    best, best_7d, source = _choose_best_price(
        craft_price=2.0, craft_price_7d=2.1, market_price=1.5, market_price_7d=1.6
    )

    assert best == 1.5
    assert best_7d == 1.6
    assert source == "auction"


@pytest.mark.unit
def test_choose_best_price_only_craft_available():
    """Test that craft is chosen when market unavailable."""
    best, best_7d, source = _choose_best_price(
        craft_price=1.0, craft_price_7d=1.1, market_price=None, market_price_7d=None
    )

    assert best == 1.0
    assert source == "crafted"


@pytest.mark.unit
def test_choose_best_price_only_market_available():
    """Test that market is chosen when craft unavailable."""
    best, best_7d, source = _choose_best_price(
        craft_price=None, craft_price_7d=None, market_price=1.5, market_price_7d=1.6
    )

    assert best == 1.5
    assert source == "auction"


@pytest.mark.unit
def test_choose_best_price_neither_available():
    """Test handling when neither craft nor market available."""
    best, best_7d, source = _choose_best_price(
        craft_price=None, craft_price_7d=None, market_price=None, market_price_7d=None
    )

    assert best is None
    assert best_7d is None
    assert source == "missing"


@pytest.mark.unit
def test_calculate_crafting_cost_simple_recipe(sample_market_data):
    """Test calculating cost for a simple recipe with vendor and market items."""
    df = sample_market_data
    lookup = build_recipe_lookup()

    # Greater Fire Protection Potion uses vendor vials and market herbs
    recipe = lookup["13457"]
    result = calculate_crafting_cost(recipe, df)

    assert result["recipe_name"] == "Greater Fire Protection Potion"
    assert result["total_cost"] > 0
    assert result["total_cost_7d"] > 0
    assert result["current_price"] is not None
    assert isinstance(result["reagent_costs"], list)
    assert len(result["reagent_costs"]) == 4  # 4 reagents


@pytest.mark.unit
def test_calculate_crafting_cost_recursive_recipe(sample_market_data):
    """Test recursive costing for Potion of Quickness (uses Swiftness Potion)."""
    df = sample_market_data
    lookup = build_recipe_lookup()

    recipe = lookup["61181"]  # Potion of Quickness
    result = calculate_crafting_cost(recipe, df)

    assert result["recipe_name"] == "Potion of Quickness"
    assert result["total_cost"] > 0

    # Find Swiftness Potion in reagent costs
    swiftness = None
    for reagent in result["reagent_costs"]:
        if reagent["name"] == "Swiftness Potion":
            swiftness = reagent
            break

    assert swiftness is not None
    # Should be either 'crafted' or 'auction' depending on which is cheaper
    assert swiftness["source"] in ["crafted", "auction"]


@pytest.mark.unit
def test_vendor_items_in_recipes(sample_market_data):
    """Test that vendor items are correctly priced and marked in recipes."""
    df = sample_market_data
    lookup = build_recipe_lookup()

    # Test Crystal Vial in Greater Fire Protection Potion
    recipe1 = lookup["13457"]
    result1 = calculate_crafting_cost(recipe1, df)
    crystal_vial = next(
        (r for r in result1["reagent_costs"] if r["name"] == "Crystal Vial"), None
    )
    assert crystal_vial is not None
    assert crystal_vial["source"] == "vendor"
    assert crystal_vial["unit_price"] == 0.2

    # Test Leaded Vial in Swiftness Potion
    recipe2 = lookup["2459"]
    result2 = calculate_crafting_cost(recipe2, df)
    leaded_vial = next(
        (r for r in result2["reagent_costs"] if r["name"] == "Leaded Vial"), None
    )
    assert leaded_vial is not None
    assert leaded_vial["source"] == "vendor"
    assert leaded_vial["unit_price"] == 0.04


@pytest.mark.unit
def test_profit_calculation(sample_market_data):
    """Test that profit is calculated correctly."""
    df = sample_market_data
    lookup = build_recipe_lookup()

    recipe = lookup["13457"]  # Greater Fire Protection Potion
    result = calculate_crafting_cost(recipe, df)

    if result["profit"] is not None:
        expected_profit = result["current_price"] - result["total_cost"]
        assert abs(result["profit"] - expected_profit) < 0.01

        expected_pct = (expected_profit / result["total_cost"]) * 100
        assert abs(result["profit_pct"] - expected_pct) < 0.1


@pytest.mark.unit
def test_get_profitable_recipes(sample_market_data):
    """Test getting list of profitable recipes."""
    df = sample_market_data

    # Get recipes with any profit
    profitable = get_profitable_recipes(df, min_profit_pct=0)

    assert isinstance(profitable, list)
    # Should have some profitable recipes in our test data
    assert len(profitable) > 0

    # Check that results are sorted by profit (descending)
    if len(profitable) > 1:
        for i in range(len(profitable) - 1):
            assert profitable[i]["profit"] >= profitable[i + 1]["profit"]


@pytest.mark.unit
def test_get_profitable_recipes_high_threshold(sample_market_data):
    """Test filtering recipes by profit threshold."""
    df = sample_market_data

    low_threshold = get_profitable_recipes(df, min_profit_pct=0)
    high_threshold = get_profitable_recipes(df, min_profit_pct=50)

    # High threshold should have fewer or equal recipes
    assert len(high_threshold) <= len(low_threshold)


@pytest.mark.unit
def test_missing_reagent_prices():
    """Test handling of recipes with missing market data."""
    # Create minimal dataframe with only one item
    dates = pd.date_range(start="2025-10-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "item_name": ["Gromsblood"] * 10,
            "avg_price": [0.5] * 10,
        },
        index=dates,
    )

    lookup = build_recipe_lookup()
    recipe = lookup["13457"]  # Greater Fire Protection Potion
    result = calculate_crafting_cost(recipe, df)

    # Should have missing prices for most reagents
    assert len(result["missing_prices"]) > 0
    assert isinstance(result["missing_prices"], list)


@pytest.mark.unit
def test_recipe_with_quantities(sample_market_data):
    """Test that reagent quantities are correctly multiplied in cost."""
    df = sample_market_data
    lookup = build_recipe_lookup()

    # Elixir of the Mongoose uses 2x Gromsblood and 2x Plaguebloom
    recipe = lookup["13452"]
    result = calculate_crafting_cost(recipe, df)

    gromsblood = None
    for reagent in result["reagent_costs"]:
        if reagent["name"] == "Gromsblood":
            gromsblood = reagent
            break

    assert gromsblood is not None
    assert gromsblood["quantity"] == 2
    expected_cost = gromsblood["unit_price"] * 2
    assert abs(gromsblood["total_cost"] - expected_cost) < 0.01
