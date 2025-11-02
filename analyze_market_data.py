import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
import json

console = Console()

DATA_DIR = Path("data/market_data/ambershire")
ITEMS_FILE = Path("data/items.json")


def load_items():
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["items"]


def analyze_item(item_id: int, item_name: str):
    """Analyze market data for a specific item and print summary statistics."""
    file_path = DATA_DIR / f"item_{item_id}_{item_name}_last_30d.csv"
    if not file_path.exists():
        console.print(f"[red]Data file for item ID {item_id} does not exist.[/red]")
        return

    # Read CSV with explicit column names to ensure correct parsing
    df = pd.read_csv(
        file_path,
        names=["timestamp", "bid", "min_buy", "avg_price", "available"],
        header=0,  # First row contains headers
        index_col="timestamp",
        parse_dates=True,
    )

    # Average over full period (30d)
    avg_30d = df["avg_price"].mean()

    # Last 7d average
    last_7d = df[df.index >= (df.index.max() - pd.Timedelta(days=7))]
    avg_7d = last_7d["avg_price"].mean()

    # Trend 7-day vs 30-day
    if avg_7d and avg_30d:
        trend = ((avg_7d - avg_30d) / avg_30d) * 100
    else:
        trend = 0

    return {
        "item_id": item_id,
        "item_name": item_name,
        "avg_30d": avg_30d,
        "avg_7d": avg_7d,
        "trend": trend,
    }


def main():
    items = load_items()

    table = Table(title="Auction House Market Summary last 30d (Ambershire)")
    table.add_column("Item", justify="left")
    table.add_column("Avg (30d)", justify="right")
    table.add_column("Avg (7d)", justify="right")
    table.add_column("7d vs 30d", justify="right")

    for item_id, item_name in items.items():
        stats = analyze_item(item_id, item_name)
        if not stats:
            continue

        trend_color = (
            "green" if stats["trend"] > 0 else "red" if stats["trend"] < 0 else "white"
        )
        table.add_row(
            stats["item_name"],
            f"{stats['avg_30d']:,.0f}",
            f"{stats['avg_7d']:,.0f}" if stats["avg_7d"] else "N/A",
            f"[{trend_color}]{stats['trend']:+.2f}%[/{trend_color}]",
        )

    console.print(table)


if __name__ == "__main__":
    main()
