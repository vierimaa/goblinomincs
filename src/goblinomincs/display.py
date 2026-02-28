"""Rich terminal display functions for all market analysis views.

All functions in this module produce console output. Calculation logic lives
in market_analysis.py; this module only handles presentation.
"""

import pandas as pd
from rich.console import Console
from rich.table import Table

from goblinomincs.market_analysis import (
    analyze_item,
    get_buy_sell_opportunities,
    get_recipes_by_source,
)
from goblinomincs.recipe_analysis import get_profitable_recipes

console = Console()


# ---------------------------------------------------------------------------
# Buy / Sell Opportunities
# ---------------------------------------------------------------------------


def display_buy_sell_opportunities(
    buy_opportunities: list[dict],
    sell_opportunities: list[dict],
    console: Console,
    max_display: int = 15,
) -> None:
    """Render buy and sell opportunity tables to the console.

    Args:
        buy_opportunities: List of buy opportunity analysis dicts
        sell_opportunities: List of sell opportunity analysis dicts
        console: Rich Console instance for output
        max_display: Maximum number of items to show per table (default: 15)
    """
    console.print("\n")
    buy_table = Table(
        title="BUY NOW - Items Cheaper Than 3-Day Average", title_style="bold green"
    )
    buy_table.add_column("Item", justify="left", style="cyan")
    buy_table.add_column("Current Price", justify="right")
    buy_table.add_column("3-Day Avg", justify="right")
    buy_table.add_column("Difference", justify="right")
    buy_table.add_column("% Off", justify="right", style="green")
    buy_table.add_column("Last Updated", justify="right", style="dim")

    for opp in sorted(buy_opportunities, key=lambda x: x["item_name"])[:max_display]:
        buy_table.add_row(
            opp["item_name"],
            f"{opp['current_price']:.2f}g",
            f"{opp['avg_3d']:.2f}g",
            f"{opp['price_diff']:.2f}g",
            f"{abs(opp['pct_diff']):.1f}%",
            opp["last_updated"].strftime("%b %d %H:%M"),
        )

    if buy_opportunities:
        console.print(buy_table)
    else:
        console.print("[yellow]No significant buy opportunities right now.[/yellow]")

    console.print("\n")
    sell_table = Table(
        title="SELL NOW - Items More Expensive Than 3-Day Average",
        title_style="bold yellow",
    )
    sell_table.add_column("Item", justify="left", style="cyan")
    sell_table.add_column("Current Price", justify="right")
    sell_table.add_column("3-Day Avg", justify="right")
    sell_table.add_column("Difference", justify="right")
    sell_table.add_column("% Premium", justify="right", style="yellow")
    sell_table.add_column("Last Updated", justify="right", style="dim")

    for opp in sorted(sell_opportunities, key=lambda x: x["item_name"])[:max_display]:
        sell_table.add_row(
            opp["item_name"],
            f"{opp['current_price']:.2f}g",
            f"{opp['avg_3d']:.2f}g",
            f"{opp['price_diff']:+.2f}g",
            f"{opp['pct_diff']:.1f}%",
            opp["last_updated"].strftime("%b %d %H:%M"),
        )

    if sell_opportunities:
        console.print(sell_table)
    else:
        console.print("[yellow]No significant sell opportunities right now.[/yellow]")


def show_buy_sell_now_opportunities(
    df: pd.DataFrame, items: dict, console_inst: Console | None = None
) -> None:
    """Display tables showing items that are good to buy or sell right now.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to item names
        console_inst: Optional Console instance (uses module console if None)
    """
    console_to_use = console_inst or console
    buy_opps, sell_opps = get_buy_sell_opportunities(df, items)
    display_buy_sell_opportunities(buy_opps, sell_opps, console_to_use)


# ---------------------------------------------------------------------------
# Profitable Crafts
# ---------------------------------------------------------------------------


def display_profitable_crafts(
    profitable: list[dict],
    console: Console,
    max_display: int = 15,
    show_details: bool = True,
) -> None:
    """Render a table of profitable crafting opportunities.

    Args:
        profitable: List of profitable recipe analysis dicts
        console: Rich Console instance for output
        max_display: Maximum number of recipes to show (default: 15)
        show_details: Whether to show detailed breakdown of top recipe (default: True)
    """
    if not profitable:
        console.print("\n[yellow]No profitable recipes found.[/yellow]")
        return

    console.print("\n")
    craft_table = Table(title="PROFITABLE CRAFTS", title_style="bold magenta")
    craft_table.add_column("Recipe", justify="left", style="cyan")
    craft_table.add_column("Craft Cost", justify="right")
    craft_table.add_column("Cost (7d avg)", justify="right", style="dim")
    craft_table.add_column("Sell Price", justify="right")
    craft_table.add_column("Price (7d avg)", justify="right", style="dim")
    craft_table.add_column("Profit", justify="right")
    craft_table.add_column("ROI", justify="right", style="yellow")

    for craft in sorted(profitable, key=lambda x: x["recipe_name"])[:max_display]:
        profit_color = (
            "green"
            if craft["profit"] > 1
            else "yellow"
            if craft["profit"] > 0.5
            else "white"
        )
        craft_table.add_row(
            craft["recipe_name"],
            f"{craft['total_cost']:.2f}g",
            f"{craft['total_cost_7d']:.2f}g",
            f"{craft['current_price']:.2f}g",
            f"{craft['current_price_7d']:.2f}g",
            f"[{profit_color}]{craft['profit']:+.2f}g[/{profit_color}]",
            f"{craft['profit_pct']:+.1f}%",
        )

    console.print(craft_table)

    if show_details and profitable:
        console.print("\n[bold cyan]Top Recipe Details:[/bold cyan]")
        top = profitable[0]
        console.print(
            f"[cyan]{top['recipe_name']}[/cyan] "
            f"(Profit: [green]{top['profit']:.2f}g[/green], "
            f"ROI: [yellow]{top['profit_pct']:.1f}%[/yellow])"
        )
        console.print("\nReagent Costs (Current / 7d avg):")
        for reagent in top["reagent_costs"]:
            source_label = "[VENDOR]" if reagent["source"] == "vendor" else "[MARKET]"
            if reagent["source"] == "vendor":
                console.print(
                    f"  {source_label} {reagent['quantity']}x {reagent['name']}: "
                    f"{reagent['unit_price']:.2f}g each = {reagent['total_cost']:.2f}g"
                )
            else:
                price_diff = (
                    (reagent["unit_price"] - reagent["unit_price_7d"])
                    / reagent["unit_price_7d"]
                    * 100
                )
                price_color = (
                    "green" if price_diff < -5 else "red" if price_diff > 5 else "white"
                )
                console.print(
                    f"  {source_label} {reagent['quantity']}x {reagent['name']}: "
                    f"[{price_color}]{reagent['unit_price']:.2f}g[/{price_color}] / "
                    f"{reagent['unit_price_7d']:.2f}g = {reagent['total_cost']:.2f}g"
                )
        console.print(
            f"\n[bold]Total Cost:[/bold] {top['total_cost']:.2f}g "
            f"(7d avg: {top['total_cost_7d']:.2f}g)"
        )
        console.print(
            f"[bold]Sell For:[/bold] {top['current_price']:.2f}g "
            f"(7d avg: {top['current_price_7d']:.2f}g)"
        )
        console.print(
            f"[bold green]Profit:[/bold green] {top['profit']:.2f}g per craft "
            f"(7d avg profit: {top['profit_7d']:.2f}g)"
        )


def show_profitable_crafts(
    df: pd.DataFrame,
    min_profit_pct: float = 5,
    console_inst: Console | None = None,
) -> None:
    """Display a table of profitable crafting opportunities.

    Args:
        df: DataFrame with all market data
        min_profit_pct: Minimum profit percentage to include (default: 5)
        console_inst: Optional Console instance (uses module console if None)
    """
    console_to_use = console_inst or console
    profitable = get_profitable_recipes(df, min_profit_pct)
    display_profitable_crafts(profitable, console_to_use)


# ---------------------------------------------------------------------------
# Recipes by Profession
# ---------------------------------------------------------------------------


def display_recipes_by_source(
    recipes_by_source: dict[str, list[dict]], console: Console
) -> None:
    """Render recipe tables organised by source (profession).

    Args:
        recipes_by_source: Dictionary mapping source names to recipe analysis lists
        console: Rich Console instance for output
    """
    for source, source_recipes in sorted(recipes_by_source.items()):
        console.print(f"\n[bold cyan]{source}[/bold cyan]")

        table = Table(
            title=f"{source} Recipes - Cost Analysis",
            title_style="cyan",
        )
        table.add_column("Recipe", justify="left", style="white")
        table.add_column("Craft Cost", justify="right")
        table.add_column("Market Price", justify="right")
        table.add_column("Profit", justify="right")
        table.add_column("ROI %", justify="right")
        table.add_column("Status", justify="center")

        for analysis in sorted(source_recipes, key=lambda x: x["recipe_name"]):
            if analysis["current_price"] is None:
                table.add_row(
                    analysis["recipe_name"],
                    f"{analysis['total_cost']:.2f}g"
                    if analysis["total_cost"] > 0
                    else "N/A",
                    "[dim]No data[/dim]",
                    "—",
                    "—",
                    "[dim]❌[/dim]",
                )
                continue

            if analysis["missing_prices"]:
                missing_count = len(analysis["missing_prices"])
                table.add_row(
                    analysis["recipe_name"],
                    f"[dim]{analysis['total_cost']:.2f}g+[/dim]",
                    f"{analysis['current_price']:.2f}g",
                    "[dim]Incomplete[/dim]",
                    "—",
                    f"[yellow]⚠ {missing_count}[/yellow]",
                )
                continue

            profit = analysis["profit"]
            roi = analysis["profit_pct"]

            profit_color = "green" if profit > 1 else "yellow" if profit > 0 else "red"
            roi_color = (
                "green"
                if roi > 20
                else "yellow"
                if roi > 5
                else "white"
                if roi > 0
                else "red"
            )
            status_icon = "✓" if profit > 0 else "✗"
            status_color = "green" if profit > 0 else "red"

            table.add_row(
                analysis["recipe_name"],
                f"{analysis['total_cost']:.2f}g",
                f"{analysis['current_price']:.2f}g",
                f"[{profit_color}]{profit:+.2f}g[/{profit_color}]",
                f"[{roi_color}]{roi:+.1f}%[/{roi_color}]",
                f"[{status_color}]{status_icon}[/{status_color}]",
            )

        console.print(table)

    console.print(
        "\n[dim]Status: ✓ = Profitable | ✗ = Loss | ⚠ = Missing reagent prices | ❌ = No market data[/dim]"
    )


def show_recipes_by_source(
    df: pd.DataFrame, console_inst: Console | None = None
) -> None:
    """Display all recipes organised by source (profession) with costs and prices.

    Args:
        df: DataFrame with all market data
        console_inst: Optional Console instance (uses module console if None)
    """
    console_to_use = console_inst or console
    recipes_by_source = get_recipes_by_source(df)
    display_recipes_by_source(recipes_by_source, console_to_use)


# ---------------------------------------------------------------------------
# Market Summary
# ---------------------------------------------------------------------------


def get_market_summary_tables(df: pd.DataFrame, items: dict) -> dict[str, Table]:
    """Build Rich market summary tables split by item category.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to nested objects:
            {id: {"name": ..., "category": ...}}

    Returns:
        dict: Mapping category -> Rich Table with market summary rows,
              sorted alphabetically by category
    """
    category_tables: dict[str, Table] = {}

    def _ensure_table(category: str) -> Table:
        if category not in category_tables:
            table = Table(
                title=f"Auction House Market Summary - {category} - Last 30 Days (Ambershire)"
            )
            table.add_column("Item", justify="left")
            table.add_column("Current Price", justify="left")
            table.add_column("Avg (30d)", justify="right")
            table.add_column("Avg (7d)", justify="right")
            table.add_column("7d vs 30d", justify="right")
            table.add_column("Best Buy", justify="right")
            table.add_column("Best Sell", justify="right")
            table.add_column("Gold Profit", justify="right")
            table.add_column("Flip Profit", justify="right")
            category_tables[category] = table
        return category_tables[category]

    # Collect rows per category, then sort by item name before adding to table
    category_rows: dict[str, list] = {}

    for item_info in items.values():
        item_name = item_info["name"]
        item_category = item_info["category"]

        stats = analyze_item(df, item_name)
        if not stats:
            continue

        trend_color = (
            "green" if stats["trend"] > 0 else "red" if stats["trend"] < 0 else "white"
        )
        flip_color = (
            "green"
            if stats["flip_profit"] > 10
            else "yellow"
            if stats["flip_profit"] > 5
            else "white"
        )

        gold_profit = stats["best_sell_price"] - stats["best_buy_price"]
        gold_color = (
            "green" if gold_profit > 1 else "yellow" if gold_profit > 0.5 else "white"
        )

        row = (
            stats["item_name"],
            f"{stats['latest_price']:.2f}g",
            f"{stats['avg_30d']:.2f}g",
            f"{stats['avg_7d']:.2f}g" if stats["avg_7d"] else "N/A",
            f"[{trend_color}]{stats['trend']:+.2f}%[/{trend_color}]",
            f"{stats['best_buy_day'][:3]} ({stats['best_buy_price']:.2f}g)",
            f"{stats['best_sell_day'][:3]} ({stats['best_sell_price']:.2f}g)",
            f"[{gold_color}]{gold_profit:+.2f}g[/{gold_color}]",
            f"[{flip_color}]{stats['flip_profit']:+.1f}%[/{flip_color}]",
        )
        category_rows.setdefault(item_category, []).append(row)

    for category, rows in category_rows.items():
        table = _ensure_table(category)
        for row in sorted(rows):
            table.add_row(*row)

    return {category: category_tables[category] for category in sorted(category_tables)}


def show_market_summary(
    df: pd.DataFrame, items: dict, console_inst: Console | None = None
) -> None:
    """Display market summary tables split by item category.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to nested objects:
            {id: {"name": ..., "category": ...}}
        console_inst: Optional Console instance (uses module console if None)
    """
    from rich.panel import Panel

    console_to_use = console_inst or console
    category_tables = get_market_summary_tables(df, items)
    for category, table in category_tables.items():
        console_to_use.print(
            Panel(f"[bold]{category}[/bold]", title=None, border_style="cyan")
        )
        console_to_use.print(table)


# ---------------------------------------------------------------------------
# Current Market
# ---------------------------------------------------------------------------


def get_current_market_tables(df: pd.DataFrame, items: dict) -> dict[str, Table]:
    """Build Rich current market tables split by item category.

    Shows current prices alongside 7-day and 30-day averages, and two
    trend columns: current price vs 7-day average, and 7-day vs 30-day average.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to nested objects:
            {id: {"name": ..., "category": ...}}

    Returns:
        dict: Mapping category -> Rich Table with current market rows,
              sorted alphabetically by category
    """
    category_tables: dict[str, Table] = {}

    def _ensure_table(category: str) -> Table:
        if category not in category_tables:
            table = Table(title=f"Current Market - {category} (Ambershire)")
            table.add_column("Item", justify="left")
            table.add_column("Current Price", justify="right")
            table.add_column("7d Avg", justify="right")
            table.add_column("30d Avg", justify="right")
            table.add_column("Current vs 7d", justify="right")
            table.add_column("7d vs 30d", justify="right")
            category_tables[category] = table
        return category_tables[category]

    category_rows: dict[str, list] = {}

    for item_info in items.values():
        item_name = item_info["name"]
        item_category = item_info["category"]

        stats = analyze_item(df, item_name)
        if not stats:
            continue

        current_vs_7d = (
            ((stats["latest_price"] - stats["avg_7d"]) / stats["avg_7d"] * 100)
            if stats["avg_7d"]
            else 0.0
        )

        current_vs_7d_color = (
            "green" if current_vs_7d < -5 else "red" if current_vs_7d > 5 else "white"
        )
        trend_color = (
            "green" if stats["trend"] > 0 else "red" if stats["trend"] < 0 else "white"
        )

        row = (
            stats["item_name"],
            f"[{current_vs_7d_color}]{stats['latest_price']:.2f}g[/{current_vs_7d_color}]",
            f"{stats['avg_7d']:.2f}g" if stats["avg_7d"] else "N/A",
            f"{stats['avg_30d']:.2f}g",
            f"[{current_vs_7d_color}]{current_vs_7d:+.2f}%[/{current_vs_7d_color}]",
            f"[{trend_color}]{stats['trend']:+.2f}%[/{trend_color}]",
        )
        category_rows.setdefault(item_category, []).append(row)

    for category, rows in category_rows.items():
        table = _ensure_table(category)
        for row in sorted(rows):
            table.add_row(*row)

    return {category: category_tables[category] for category in sorted(category_tables)}


def show_current_market(
    df: pd.DataFrame, items: dict, console_inst: Console | None = None
) -> None:
    """Display current market tables split by item category.

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to nested objects:
            {id: {"name": ..., "category": ...}}
        console_inst: Optional Console instance (uses module console if None)
    """
    from rich.panel import Panel

    console_to_use = console_inst or console
    category_tables = get_current_market_tables(df, items)
    for category, table in category_tables.items():
        console_to_use.print(
            Panel(f"[bold]{category}[/bold]", title=None, border_style="cyan")
        )
        console_to_use.print(table)
