"""Tests for display.py - Rich table and console output functions."""

import io
from datetime import datetime
from unittest.mock import patch

import pytest
from rich.console import Console

from goblinomincs.display import (
    display_buy_sell_opportunities,
    display_profitable_crafts,
    display_recipes_by_source,
    get_current_market_tables,
    get_market_summary_tables,
    show_buy_sell_now_opportunities,
    show_current_market,
    show_market_summary,
    show_profitable_crafts,
    show_recipes_by_source,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_console() -> Console:
    """Return a Rich Console that writes to an in-memory buffer.

    width=500 prevents Rich from word-wrapping long table cell content
    across multiple lines, which would break substring assertions.
    """
    return Console(
        file=io.StringIO(),
        force_terminal=False,
        highlight=False,
        no_color=True,
        width=500,
    )


def get_output(con: Console) -> str:
    """Return all text written to the console buffer."""
    return con.file.getvalue()


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def buy_opportunity():
    """A single buy opportunity dict."""
    return {
        "item_name": "Thorium Ore",
        "current_price": 8.00,
        "avg_3d": 10.00,
        "price_diff": -2.00,
        "pct_diff": -20.0,
        "last_updated": datetime(2026, 2, 26, 12, 0),
    }


@pytest.fixture
def sell_opportunity():
    """A single sell opportunity dict."""
    return {
        "item_name": "Arcane Crystal",
        "current_price": 15.00,
        "avg_3d": 12.00,
        "price_diff": +3.00,
        "pct_diff": +25.0,
        "last_updated": datetime(2026, 2, 26, 12, 0),
    }


@pytest.fixture
def vendor_reagent():
    """A vendor-sourced reagent dict."""
    return {
        "source": "vendor",
        "quantity": 1,
        "name": "Crystal Vial",
        "unit_price": 0.20,
        "total_cost": 0.20,
    }


@pytest.fixture
def market_reagent():
    """A market-sourced reagent dict."""
    return {
        "source": "market",
        "quantity": 2,
        "name": "Gromsblood",
        "unit_price": 0.50,
        "unit_price_7d": 0.55,
        "total_cost": 1.00,
    }


@pytest.fixture
def profitable_recipe(vendor_reagent, market_reagent):
    """A profitable crafting recipe analysis dict."""
    return {
        "recipe_name": "Major Healing Potion",
        "total_cost": 1.20,
        "total_cost_7d": 1.30,
        "current_price": 3.00,
        "current_price_7d": 2.80,
        "profit": 1.80,
        "profit_pct": 150.0,
        "profit_7d": 1.50,
        "reagent_costs": [vendor_reagent, market_reagent],
        "missing_prices": [],
    }


@pytest.fixture
def items_dict():
    """Items dict with two categories for table-builder tests.

    All names must exist in the sample_market_data conftest fixture.
    """
    return {
        "1": {"name": "Gromsblood", "category": "Herbs"},
        "2": {"name": "Dreamfoil", "category": "Herbs"},
        "3": {"name": "Elemental Fire", "category": "Reagents"},
    }


@pytest.fixture
def items_with_missing(items_dict):
    """items_dict extended with an item that has no market data."""
    result = dict(items_dict)
    result["99"] = {"name": "Ghost Item XYZ", "category": "Other"}
    return result


# ---------------------------------------------------------------------------
# display_buy_sell_opportunities
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_display_buy_sell_shows_buy_table_header(buy_opportunity, sell_opportunity):
    """Table title for buy opportunities is rendered."""
    con = make_console()
    display_buy_sell_opportunities([buy_opportunity], [sell_opportunity], con)
    assert "BUY NOW" in get_output(con)


@pytest.mark.unit
def test_display_buy_sell_shows_item_names(buy_opportunity, sell_opportunity):
    """Item names appear in the rendered output."""
    con = make_console()
    display_buy_sell_opportunities([buy_opportunity], [sell_opportunity], con)
    output = get_output(con)
    assert "Thorium Ore" in output
    assert "Arcane Crystal" in output


@pytest.mark.unit
def test_display_buy_sell_shows_gold_values(buy_opportunity, sell_opportunity):
    """Gold values are formatted and present in output."""
    con = make_console()
    display_buy_sell_opportunities([buy_opportunity], [sell_opportunity], con)
    output = get_output(con)
    assert "8.00g" in output
    assert "15.00g" in output


@pytest.mark.unit
def test_display_buy_sell_empty_buy_list(sell_opportunity):
    """Fallback message shown when no buy opportunities exist."""
    con = make_console()
    display_buy_sell_opportunities([], [sell_opportunity], con)
    assert "No significant buy opportunities" in get_output(con)


@pytest.mark.unit
def test_display_buy_sell_empty_sell_list(buy_opportunity):
    """Fallback message shown when no sell opportunities exist."""
    con = make_console()
    display_buy_sell_opportunities([buy_opportunity], [], con)
    assert "No significant sell opportunities" in get_output(con)


@pytest.mark.unit
def test_display_buy_sell_max_display_limits_rows():
    """max_display caps the number of rows shown per table."""
    con = make_console()
    opps = [
        {
            "item_name": f"Item {i}",
            "current_price": 1.0,
            "avg_3d": 2.0,
            "price_diff": -1.0,
            "pct_diff": -50.0,
            "last_updated": datetime(2026, 2, 26, 12, 0),
        }
        for i in range(3)
    ]
    display_buy_sell_opportunities(opps, [], con, max_display=1)
    output = get_output(con)
    # max_display=1 with sorted items: "Item 0" is first alphabetically
    assert "Item 0" in output
    assert "Item 2" not in output


# ---------------------------------------------------------------------------
# show_buy_sell_now_opportunities
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_show_buy_sell_now_uses_get_opportunities(
    sample_market_data, buy_opportunity, sell_opportunity
):
    """show_buy_sell_now_opportunities delegates to get_buy_sell_opportunities."""
    con = make_console()
    with patch(
        "goblinomincs.display.get_buy_sell_opportunities",
        return_value=([buy_opportunity], [sell_opportunity]),
    ):
        show_buy_sell_now_opportunities(sample_market_data, {}, console_inst=con)
    output = get_output(con)
    assert "Thorium Ore" in output
    assert "Arcane Crystal" in output


# ---------------------------------------------------------------------------
# display_profitable_crafts
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_display_profitable_crafts_empty_list():
    """Empty profitable list shows fallback message."""
    con = make_console()
    display_profitable_crafts([], con)
    assert "No profitable recipes found" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_shows_table_title(profitable_recipe):
    """Table title and recipe name are rendered."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=False)
    output = get_output(con)
    assert "PROFITABLE CRAFTS" in output
    assert "Major Healing Potion" in output


@pytest.mark.unit
def test_display_profitable_crafts_no_details_when_disabled(profitable_recipe):
    """Details section is absent when show_details=False."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=False)
    assert "Top Recipe Details" not in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_shows_details_header(profitable_recipe):
    """Details section header appears when show_details=True."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=True)
    assert "Top Recipe Details" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_shows_vendor_reagent(profitable_recipe):
    """Vendor reagent name appears in the details section."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=True)
    assert "Crystal Vial" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_shows_market_reagent(profitable_recipe):
    """Market reagent name appears in the details section."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=True)
    assert "Gromsblood" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_shows_total_cost_line(profitable_recipe):
    """Total Cost line is printed in the details section."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=True)
    assert "Total Cost:" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_high_profit_shown(profitable_recipe):
    """Profit value with leading '+' sign is present in output."""
    con = make_console()
    display_profitable_crafts([profitable_recipe], con, show_details=False)
    assert "+1.80g" in get_output(con)


@pytest.mark.unit
def test_display_profitable_crafts_yellow_profit_threshold():
    """Recipe with profit between 0.5 and 1.0 renders without error."""
    con = make_console()
    recipe = {
        "recipe_name": "Minor Potion",
        "total_cost": 1.0,
        "total_cost_7d": 1.1,
        "current_price": 1.75,
        "current_price_7d": 1.6,
        "profit": 0.75,
        "profit_pct": 75.0,
        "profit_7d": 0.5,
        "reagent_costs": [],
        "missing_prices": [],
    }
    display_profitable_crafts([recipe], con, show_details=False)
    output = get_output(con)
    assert "Minor Potion" in output
    assert "+0.75g" in output


@pytest.mark.unit
def test_display_profitable_crafts_low_profit_threshold():
    """Recipe with profit <= 0.5 renders without error (white colour branch)."""
    con = make_console()
    recipe = {
        "recipe_name": "Weak Potion",
        "total_cost": 1.0,
        "total_cost_7d": 1.1,
        "current_price": 1.40,
        "current_price_7d": 1.3,
        "profit": 0.40,
        "profit_pct": 40.0,
        "profit_7d": 0.3,
        "reagent_costs": [],
        "missing_prices": [],
    }
    display_profitable_crafts([recipe], con, show_details=False)
    assert "Weak Potion" in get_output(con)


# ---------------------------------------------------------------------------
# show_profitable_crafts
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_show_profitable_crafts_calls_get_profitable(
    sample_market_data, profitable_recipe
):
    """show_profitable_crafts delegates to get_profitable_recipes."""
    con = make_console()
    with patch(
        "goblinomincs.display.get_profitable_recipes",
        return_value=[profitable_recipe],
    ):
        show_profitable_crafts(sample_market_data, console_inst=con)
    assert "Major Healing Potion" in get_output(con)


# ---------------------------------------------------------------------------
# display_recipes_by_source fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def analysis_no_market_data():
    """Recipe analysis where market data is completely absent."""
    return {
        "recipe_name": "Ghost Recipe",
        "current_price": None,
        "missing_prices": [],
        "total_cost": 0.0,
        "profit": 0.0,
        "profit_pct": 0.0,
    }


@pytest.fixture
def analysis_missing_prices():
    """Recipe analysis where some reagent prices are missing."""
    return {
        "recipe_name": "Partial Recipe",
        "current_price": 5.0,
        "missing_prices": ["Reagent A", "Reagent B"],
        "total_cost": 2.0,
        "profit": 0.0,
        "profit_pct": 0.0,
    }


@pytest.fixture
def analysis_profitable():
    """Recipe analysis that is profitable (profit > 0)."""
    return {
        "recipe_name": "Good Recipe",
        "current_price": 5.0,
        "missing_prices": [],
        "total_cost": 3.0,
        "profit": 2.0,
        "profit_pct": 66.7,
    }


@pytest.fixture
def analysis_loss():
    """Recipe analysis that results in a loss (profit < 0)."""
    return {
        "recipe_name": "Bad Recipe",
        "current_price": 1.0,
        "missing_prices": [],
        "total_cost": 3.0,
        "profit": -2.0,
        "profit_pct": -66.7,
    }


# ---------------------------------------------------------------------------
# display_recipes_by_source
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_display_recipes_no_market_data_shows_no_data(analysis_no_market_data):
    """Row shows 'No data' when current_price is None."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_no_market_data]}, con)
    assert "No data" in get_output(con)


@pytest.mark.unit
def test_display_recipes_missing_prices_shows_warning_count(analysis_missing_prices):
    """Row shows missing reagent count when missing_prices is non-empty."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_missing_prices]}, con)
    output = get_output(con)
    # The missing count (2) should appear somewhere in the row
    assert "2" in output


@pytest.mark.unit
def test_display_recipes_missing_prices_shows_recipe_name(analysis_missing_prices):
    """Recipe name is shown even when prices are missing."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_missing_prices]}, con)
    assert "Partial Recipe" in get_output(con)


@pytest.mark.unit
def test_display_recipes_profitable_shows_checkmark(analysis_profitable):
    """Profitable recipe shows a checkmark (✓) status icon."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_profitable]}, con)
    assert "✓" in get_output(con)


@pytest.mark.unit
def test_display_recipes_loss_shows_cross(analysis_loss):
    """Loss recipe shows a cross (✗) status icon."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_loss]}, con)
    assert "✗" in get_output(con)


@pytest.mark.unit
def test_display_recipes_shows_status_legend(analysis_profitable):
    """Status legend line is always printed at the bottom."""
    con = make_console()
    display_recipes_by_source({"Alchemy": [analysis_profitable]}, con)
    assert "Profitable" in get_output(con)


@pytest.mark.unit
def test_display_recipes_shows_profession_name(analysis_profitable):
    """The profession / source name appears above the table."""
    con = make_console()
    display_recipes_by_source({"Engineering": [analysis_profitable]}, con)
    assert "Engineering" in get_output(con)


@pytest.mark.unit
def test_display_recipes_multiple_sources_rendered(analysis_profitable, analysis_loss):
    """Multiple profession sections are all rendered."""
    con = make_console()
    display_recipes_by_source(
        {"Alchemy": [analysis_profitable], "Blacksmithing": [analysis_loss]}, con
    )
    output = get_output(con)
    assert "Alchemy" in output
    assert "Blacksmithing" in output


# ---------------------------------------------------------------------------
# show_recipes_by_source
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_show_recipes_by_source_calls_get_recipes(
    sample_market_data, analysis_profitable
):
    """show_recipes_by_source delegates to get_recipes_by_source."""
    con = make_console()
    with patch(
        "goblinomincs.display.get_recipes_by_source",
        return_value={"Alchemy": [analysis_profitable]},
    ):
        show_recipes_by_source(sample_market_data, console_inst=con)
    output = get_output(con)
    assert "Alchemy" in output
    assert "Good Recipe" in output


# ---------------------------------------------------------------------------
# get_market_summary_tables
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_market_summary_tables_returns_expected_categories(
    sample_market_data, items_dict
):
    """Returned dict contains both expected category keys."""
    tables = get_market_summary_tables(sample_market_data, items_dict)
    assert "Herbs" in tables
    assert "Reagents" in tables


@pytest.mark.unit
def test_get_market_summary_tables_sorted_categories(sample_market_data, items_dict):
    """Categories are returned in alphabetical order."""
    tables = get_market_summary_tables(sample_market_data, items_dict)
    assert list(tables.keys()) == sorted(tables.keys())


@pytest.mark.unit
def test_get_market_summary_tables_correct_column_count(sample_market_data, items_dict):
    """Each table has exactly 9 columns."""
    tables = get_market_summary_tables(sample_market_data, items_dict)
    assert len(tables["Herbs"].columns) == 9


@pytest.mark.unit
def test_get_market_summary_tables_herb_row_count(sample_market_data, items_dict):
    """Row count matches the number of Herbs items with available data."""
    tables = get_market_summary_tables(sample_market_data, items_dict)
    # items_dict has 2 Herbs items (Gromsblood, Dreamfoil), both in sample_market_data
    assert tables["Herbs"].row_count == 2


@pytest.mark.unit
def test_get_market_summary_tables_skips_missing_items(
    sample_market_data, items_with_missing
):
    """Items with no market data are skipped; their category is omitted."""
    tables = get_market_summary_tables(sample_market_data, items_with_missing)
    assert "Other" not in tables


# ---------------------------------------------------------------------------
# get_current_market_tables
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_current_market_tables_returns_expected_categories(
    sample_market_data, items_dict
):
    """Returned dict contains both expected category keys."""
    tables = get_current_market_tables(sample_market_data, items_dict)
    assert "Herbs" in tables
    assert "Reagents" in tables


@pytest.mark.unit
def test_get_current_market_tables_sorted_categories(sample_market_data, items_dict):
    """Categories are returned in alphabetical order."""
    tables = get_current_market_tables(sample_market_data, items_dict)
    assert list(tables.keys()) == sorted(tables.keys())


@pytest.mark.unit
def test_get_current_market_tables_column_count(sample_market_data, items_dict):
    """Each table has exactly 6 columns."""
    tables = get_current_market_tables(sample_market_data, items_dict)
    assert len(tables["Herbs"].columns) == 6


@pytest.mark.unit
def test_get_current_market_tables_herb_row_count(sample_market_data, items_dict):
    """Row count matches the number of Herbs items with available data."""
    tables = get_current_market_tables(sample_market_data, items_dict)
    assert tables["Herbs"].row_count == 2


@pytest.mark.unit
def test_get_current_market_tables_skips_missing_items(
    sample_market_data, items_with_missing
):
    """Items with no market data are skipped; their category is omitted."""
    tables = get_current_market_tables(sample_market_data, items_with_missing)
    assert "Other" not in tables


# ---------------------------------------------------------------------------
# show_market_summary
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_show_market_summary_outputs_category_panel(sample_market_data, items_dict):
    """Category name appears in the panel output."""
    con = make_console()
    show_market_summary(sample_market_data, items_dict, console_inst=con)
    assert "Herbs" in get_output(con)


@pytest.mark.unit
def test_show_market_summary_outputs_table_title(sample_market_data, items_dict):
    """Table title text is present in output."""
    con = make_console()
    show_market_summary(sample_market_data, items_dict, console_inst=con)
    assert "Auction House Market Summary" in get_output(con)


# ---------------------------------------------------------------------------
# show_current_market
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_show_current_market_outputs_category_panel(sample_market_data, items_dict):
    """Category name appears in the panel output."""
    con = make_console()
    show_current_market(sample_market_data, items_dict, console_inst=con)
    assert "Herbs" in get_output(con)


@pytest.mark.unit
def test_show_current_market_outputs_table_title(sample_market_data, items_dict):
    """Table title text is present in output."""
    con = make_console()
    show_current_market(sample_market_data, items_dict, console_inst=con)
    assert "Current Market" in get_output(con)
