"""Tests for CLI presentation logic."""

from rich.table import Table

import pytest

from goblinomincs.cli import build_market_summary_table


@pytest.mark.integration
def test_market_summary_split_by_category(sample_market_data):
    """Expect market summary to be split into tables per item category.

    This test asserts the function returns a mapping from category name
    to a Rich `Table` for each category present in the input items map.
    """
    df = sample_market_data

    # Construct items mapping with nested objects (id -> {name, category})
    items_map = {
        "8846": {"name": "Gromsblood", "category": "Herbalism"},
        "13465": {"name": "Mountain Silversage", "category": "Herbalism"},
        "2459": {"name": "Swiftness Potion", "category": "Alchemy"},
    }

    result = build_market_summary_table(df, items_map)

    # Desired behaviour: return a dict mapping category -> Table
    assert isinstance(result, dict)
    assert "Herbalism" in result and "Alchemy" in result
    for tbl in result.values():
        assert isinstance(tbl, Table)
