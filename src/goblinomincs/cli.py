"""CLI interface for WoW Gold market analysis."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from goblinomincs.display import (
    show_buy_sell_now_opportunities,
    show_market_summary,
    show_profitable_crafts,
    show_recipes_by_source,
)
from goblinomincs.market_loader import load_all_market_data, load_items

console = Console()


def interactive_menu():
    """Run an interactive menu that lets users choose analysis views."""
    # Load data once at startup
    console.print("\n[bold cyan]Goblinomincs - Market Analysis Tool[/bold cyan]")
    console.print("[cyan]Loading market data...[/cyan]")
    df = load_all_market_data()
    items_map = load_items()
    # name-only mapping for other functions
    items = {item_id: item_info["name"] for item_id, item_info in items_map.items()}
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
            # Market Summary (split by category)
            show_market_summary(df, items_map)

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
            show_market_summary(df, items_map)

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
