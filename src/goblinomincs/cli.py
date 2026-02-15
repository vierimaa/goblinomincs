"""CLI interface for WoW Gold AI market analysis."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from goblinomincs.analyze_market_data import (
    analyze_item,
    show_buy_sell_now_opportunities,
    show_profitable_crafts,
    show_recipes_by_source,
)
from goblinomincs.market_data import load_all_market_data, load_item_names

console = Console()


def build_market_summary_table(df, items: dict) -> Table:
    """Build market summary table (reusable across views).

    Args:
        df: DataFrame with all market data
        items: Dictionary mapping item IDs to item names

    Returns:
        Table: Rich table with market summary data
    """
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

    return table


def interactive_menu():
    """Run an interactive menu that lets users choose analysis views."""
    # Load data once at startup
    console.print("\n[bold cyan]Goblinomincs - Market Analysis Tool[/bold cyan]")
    console.print("[cyan]Loading market data...[/cyan]")
    df = load_all_market_data()
    items = load_item_names()
    console.print("[green]Data loaded successfully![/green]\n")

    while True:
        # Display menu
        menu = Panel(
            "[1] Market Summary (30-day overview)\n"
            "[2] Buy/Sell Opportunities (immediate actions)\n"
            "[3] Profitable Crafts (recipe profitability)\n"
            "[4] Recipes by Profession (all recipes organized by source)\n"
            "[5] Show All Views\n"
            "[6] Exit",
            title="[bold cyan]Select Analysis View[/bold cyan]",
            border_style="cyan",
        )
        console.print(menu)

        choice = Prompt.ask(
            "[cyan]Enter your choice[/cyan]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1",
        )

        console.print()  # Add spacing

        if choice == "1":
            # Market Summary
            table = build_market_summary_table(df, items)
            console.print(table)

        elif choice == "2":
            # Buy/Sell Opportunities
            show_buy_sell_now_opportunities(df, items)

        elif choice == "3":
            # Profitable Crafts
            min_profit = Prompt.ask(
                "[cyan]Minimum profit % to show[/cyan]",
                default="5.0",
            )
            try:
                min_profit_value = float(min_profit)
            except ValueError:
                min_profit_value = 5.0
                console.print("[yellow]Invalid input, using default (5%)[/yellow]")

            show_profitable_crafts(df, min_profit_pct=min_profit_value)

        elif choice == "4":
            # Recipes by Profession
            show_recipes_by_source(df)

        elif choice == "5":
            # Show all views
            show_buy_sell_now_opportunities(df, items)
            show_profitable_crafts(df, min_profit_pct=5.0)
            show_recipes_by_source(df)

            # Market summary
            console.print("\n")
            table = build_market_summary_table(df, items)
            console.print(table)

        elif choice == "6":
            # Exit
            console.print(
                "[cyan]Thanks for using Goblinomincs! Good luck with your gold making![/cyan]"
            )
            break

        # Pause before showing menu again
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        console.print("\n" * 2)  # Clear space for next menu


def main():
    """Entry point for the CLI."""
    interactive_menu()


if __name__ == "__main__":
    main()
