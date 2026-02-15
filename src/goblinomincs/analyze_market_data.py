import pandas as pd
from rich.console import Console
from rich.table import Table

from goblinomincs.market_data import load_all_market_data, load_item_names
from goblinomincs.recipe_analysis import (
    calculate_crafting_cost,
    get_profitable_recipes,
    load_recipes,
)

console = Console()


def analyze_daily_patterns(item_df: pd.DataFrame) -> dict:
    """Analyze which days are best for buying/selling an item.

    Args:
        item_df: DataFrame with item price data, must have 'avg_price' column and datetime index

    Returns:
        dict with best buy/sell days, prices, and potential profit percentage
    """
    # Group by day name directly from the datetime index
    daily_prices = (
        item_df.groupby(item_df.index.day_name())["avg_price"]
        .agg(["mean", "count"])
        .round(2)
    )

    # Get days with enough samples for reliable stats
    valid_days = daily_prices[daily_prices["count"] >= 3]

    if valid_days.empty:
        return {
            "best_buy_day": "N/A",
            "best_buy_price": 0,
            "best_sell_day": "N/A",
            "best_sell_price": 0,
            "potential_profit": 0,
        }

    # Find best days
    best_buy_day = valid_days.sort_values("mean").index[0]
    best_sell_day = valid_days.sort_values("mean", ascending=False).index[0]

    # Get prices and calculate profit
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
        dict with current price, 3-day average, and percentage difference
    """
    item_df = df.loc[df["item_name"] == item_name].copy()

    if item_df.empty:
        return {}

    # Get the latest price (most recent entry)
    latest_price = item_df.iloc[-1]["avg_price"]
    latest_time = item_df.index[-1]

    # Calculate 3-day average (excluding the current entry)
    three_days_ago = latest_time - pd.Timedelta(days=3)
    three_day_data = item_df.loc[
        (item_df.index >= three_days_ago) & (item_df.index < latest_time)
    ]

    if three_day_data.empty:
        return {}

    avg_3d = three_day_data["avg_price"].mean()

    # Calculate percentage difference (negative = cheaper now, positive = more expensive now)
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
        dict with analysis results including averages, trends and best trading days
    """
    # Create a clean copy for this item's analysis
    item_df = df.loc[df["item_name"] == item_name].copy()

    if item_df.empty:
        console.print(f"[red]No data found for item: {item_name}[/red]")
        return {}

    # Average over full period (30d)
    avg_30d = item_df["avg_price"].mean()

    # Calculate 7-day stats using efficient datetime indexing
    cutoff_date = item_df.index.max() - pd.Timedelta(days=7)
    avg_7d = item_df.loc[item_df.index >= cutoff_date, "avg_price"].mean()

    # Calculate trend
    trend = ((avg_7d - avg_30d) / avg_30d * 100) if avg_7d and avg_30d else 0

    # Get daily patterns
    daily_patterns = analyze_daily_patterns(item_df)

    return {
        "item_name": item_name,
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

    # Analyze all items
    for _item_id, item_name in items.items():
        analysis = analyze_buy_sell_now(df, item_name)
        if not analysis:
            continue

        # If price is lower than 3-day avg by threshold, it's a buy opportunity
        if analysis["pct_diff"] < -threshold_pct:
            buy_opportunities.append(analysis)
        # If price is higher than 3-day avg by threshold, it's a sell opportunity
        elif analysis["pct_diff"] > threshold_pct:
            sell_opportunities.append(analysis)

    # Sort by absolute gold difference (largest savings/profits first)
    buy_opportunities.sort(key=lambda x: abs(x["price_diff"]), reverse=True)
    sell_opportunities.sort(key=lambda x: x["price_diff"], reverse=True)

    return buy_opportunities, sell_opportunities


def display_buy_sell_opportunities(
    buy_opportunities: list[dict],
    sell_opportunities: list[dict],
    console: Console,
    max_display: int = 15,
) -> None:
    """Display buy and sell opportunity tables.

    Args:
        buy_opportunities: List of buy opportunity analysis dicts
        sell_opportunities: List of sell opportunity analysis dicts
        console: Rich Console instance for output
        max_display: Maximum number of items to show per table (default: 15)
    """

    # Display BUY NOW opportunities
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

    for opp in buy_opportunities[:max_display]:
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

    # Display SELL NOW opportunities
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

    for opp in sell_opportunities[:max_display]:
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


def display_profitable_crafts(
    profitable: list[dict],
    console: Console,
    max_display: int = 15,
    show_details: bool = True,
) -> None:
    """Display table showing profitable crafting opportunities.

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
    craft_table = Table(
        title="PROFITABLE CRAFTS",
        title_style="bold magenta",
    )
    craft_table.add_column("Recipe", justify="left", style="cyan")
    craft_table.add_column("Craft Cost", justify="right")
    craft_table.add_column("Cost (7d avg)", justify="right", style="dim")
    craft_table.add_column("Sell Price", justify="right")
    craft_table.add_column("Price (7d avg)", justify="right", style="dim")
    craft_table.add_column("Profit", justify="right")
    craft_table.add_column("ROI", justify="right", style="yellow")

    for craft in profitable[:max_display]:
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

    # Show detailed breakdown of top recipe
    if show_details and profitable:
        console.print("\n[bold cyan]Top Recipe Details:[/bold cyan]")
        top = profitable[0]
        console.print(
            f"[cyan]{top['recipe_name']}[/cyan] (Profit: [green]{top['profit']:.2f}g[/green], ROI: [yellow]{top['profit_pct']:.1f}%[/yellow])"
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
                    f"[{price_color}]{reagent['unit_price']:.2f}g[/{price_color}] / {reagent['unit_price_7d']:.2f}g = "
                    f"{reagent['total_cost']:.2f}g"
                )
        console.print(
            f"\n[bold]Total Cost:[/bold] {top['total_cost']:.2f}g (7d avg: {top['total_cost_7d']:.2f}g)"
        )
        console.print(
            f"[bold]Sell For:[/bold] {top['current_price']:.2f}g (7d avg: {top['current_price_7d']:.2f}g)"
        )
        console.print(
            f"[bold green]Profit:[/bold green] {top['profit']:.2f}g per craft (7d avg profit: {top['profit_7d']:.2f}g)"
        )


def show_profitable_crafts(
    df: pd.DataFrame,
    min_profit_pct: float = 5,
    console_inst: Console | None = None,
) -> None:
    """Display table showing profitable crafting opportunities.

    Args:
        df: DataFrame with all market data
        min_profit_pct: Minimum profit percentage to include (default: 5)
        console_inst: Optional Console instance (uses module console if None)
    """
    console_to_use = console_inst or console
    profitable = get_profitable_recipes(df, min_profit_pct)
    display_profitable_crafts(profitable, console_to_use)


def get_recipes_by_source(df: pd.DataFrame) -> dict[str, list[dict]]:
    """Group recipes by source (profession) with cost analysis.

    Args:
        df: DataFrame with all market data

    Returns:
        dict: Dictionary mapping source names to lists of recipe analysis dicts
    """
    recipes = load_recipes()
    recipes_by_source = {}

    for recipe in recipes:
        source = recipe.get("source", "Unknown")
        if source not in recipes_by_source:
            recipes_by_source[source] = []

        # Calculate cost analysis for this recipe
        analysis = calculate_crafting_cost(recipe, df)
        recipes_by_source[source].append(analysis)

    # Sort recipes within each source by name
    for source in recipes_by_source:
        recipes_by_source[source].sort(key=lambda r: r["recipe_name"])

    return recipes_by_source


def display_recipes_by_source(
    recipes_by_source: dict[str, list[dict]], console: Console
) -> None:
    """Display recipe tables organized by source (profession).

    Args:
        recipes_by_source: Dictionary mapping source names to recipe analysis lists
        console: Rich Console instance for output
    """

    # Display tables for each source/profession
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

        for analysis in source_recipes:
            # Handle missing prices
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

            # Full data available
            profit = analysis["profit"]
            roi = analysis["profit_pct"]

            # Color coding
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
    """Display all recipes organized by source (profession) with costs and prices.

    Args:
        df: DataFrame with all market data
        console_inst: Optional Console instance (uses module console if None)
    """
    console_to_use = console_inst or console
    recipes_by_source = get_recipes_by_source(df)
    display_recipes_by_source(recipes_by_source, console_to_use)


def main():
    # Load all market data at once
    console.print("[cyan]Loading market data...[/cyan]")
    df = load_all_market_data()

    items = load_item_names()

    # Show buy/sell now opportunities first
    show_buy_sell_now_opportunities(df, items)

    # Show profitable crafting opportunities
    show_profitable_crafts(df, min_profit_pct=5)

    # Show full market summary
    console.print("\n")
    table = Table(title="Auction House Market Summary - Last 30 Days (Ambershire)")
    table.add_column("Item", justify="left")
    table.add_column("Avg (30d)", justify="right")
    table.add_column("Avg (7d)", justify="right")
    table.add_column("7d vs 30d", justify="right")
    table.add_column("Best Buy", justify="right")
    table.add_column("Best Sell", justify="right")
    table.add_column("Gold Profit", justify="right")
    table.add_column("Flip Profit", justify="right")

    for _item_id, item_name in items.items():
        stats = analyze_item(df, item_name)
        if not stats:
            continue

        trend_color = (
            "green" if stats["trend"] > 0 else "red" if stats["trend"] < 0 else "white"
        )

        if stats["flip_profit"] > 10:
            flip_color = "green"
        elif stats["flip_profit"] > 5:
            flip_color = "yellow"
        else:
            flip_color = "white"

        # Calculate raw gold profit
        gold_profit = stats["best_sell_price"] - stats["best_buy_price"]
        gold_color = (
            "green" if gold_profit > 1 else "yellow" if gold_profit > 0.5 else "white"
        )

        table.add_row(
            stats["item_name"],
            f"{stats['avg_30d']:.2f}g",
            f"{stats['avg_7d']:.2f}g" if stats["avg_7d"] else "N/A",
            f"[{trend_color}]{stats['trend']:+.2f}%[/{trend_color}]",
            f"{stats['best_buy_day'][:3]} ({stats['best_buy_price']:.2f}g)",
            f"{stats['best_sell_day'][:3]} ({stats['best_sell_price']:.2f}g)",
            f"[{gold_color}]{gold_profit:+.2f}g[/{gold_color}]",
            f"[{flip_color}]{stats['flip_profit']:+.1f}%[/{flip_color}]",
        )

    console.print(table)


if __name__ == "__main__":
    main()
