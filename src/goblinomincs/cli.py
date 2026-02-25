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
    console.print("\n[bold cyan]Goblinomincs - Market Analysis Tool[/bold cyan]")
    console.print("[cyan]Loading market data...[/cyan]")

    try:
        items_map = load_items()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] Required file not found: {e.filename}")
        console.print("[yellow]Please ensure data/items.json exists.[/yellow]")
        return
    except KeyError as e:
        console.print(f"[red]Error:[/red] Missing expected key in items.json: {e}")
        console.print(
            "[yellow]Please check that items.json has an 'items' key.[/yellow]"
        )
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load items: {e}")
        return

    try:
        df = load_all_market_data()
    except FileNotFoundError:
        console.print("[red]Error:[/red] No market data found.")
        console.print(
            "[yellow]Please run 'uv run fetch-auction-data' to download market data first.[/yellow]"
        )
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load market data: {e}")
        return

    items = {item_id: item_info["name"] for item_id, item_info in items_map.items()}
    console.print("[green]Data loaded successfully![/green]\n")

    min_profit_value = 5.0

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
            try:
                show_market_summary(df, items_map)
            except Exception as e:
                console.print(f"[red]Error displaying market summary: {e}[/red]")

        elif choice == "2":
            try:
                show_buy_sell_now_opportunities(df, items)
            except Exception as e:
                console.print(
                    f"[red]Error displaying buy/sell opportunities: {e}[/red]"
                )

        elif choice == "3":
            min_profit = Prompt.ask(
                "[cyan]Minimum profit % to show[/cyan]",
                default="5.0",
            )
            try:
                min_profit_value = float(min_profit)
            except ValueError:
                console.print("[yellow]Invalid input, using default (5%)[/yellow]")

            try:
                show_profitable_crafts(df, min_profit_pct=min_profit_value)
            except Exception as e:
                console.print(f"[red]Error displaying profitable crafts: {e}[/red]")

        elif choice == "4":
            try:
                show_recipes_by_source(df)
            except Exception as e:
                console.print(f"[red]Error displaying recipes: {e}[/red]")

        elif choice == "5":
            try:
                show_buy_sell_now_opportunities(df, items)
            except Exception as e:
                console.print(
                    f"[red]Error displaying buy/sell opportunities: {e}[/red]"
                )

            try:
                show_profitable_crafts(df, min_profit_pct=5.0)
            except Exception as e:
                console.print(f"[red]Error displaying profitable crafts: {e}[/red]")

            try:
                show_recipes_by_source(df)
            except Exception as e:
                console.print(f"[red]Error displaying recipes: {e}[/red]")

            try:
                show_market_summary(df, items_map)
            except Exception as e:
                console.print(f"[red]Error displaying market summary: {e}[/red]")

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
