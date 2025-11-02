import json
from pathlib import Path
import requests
import pandas as pd
from rich.console import Console
from datetime import datetime, timedelta

console = Console()


def fetch_auction_history(item_id: int, realm: str = "ambershire", period: str = "30d"):
    """Fetch auction history for a specific item from wowauctions.net."""
    url = f"https://api.wowauctions.net/items/stats/{period}/{realm}/mergedAh/{item_id}"
    console.print(f"Fetching data from [cyan]{url}[/cyan]...")

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data


def is_recent(file_path: Path, hours: int = 24) -> bool:
    """Check if the file was modified within the last `hours` hours."""
    if not file_path.exists():
        return False
    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.now() - modified_time < timedelta(hours=hours)


def to_dataframe(data: dict) -> pd.DataFrame:
    """Convert API response to a Pandas DataFrame with proper datetime index."""
    df = pd.DataFrame.from_dict(data, orient="index")
    df.index = pd.to_datetime(df.index, format="%Y,%m,%d,%H")
    df.sort_index(inplace=True)
    return df


def save_to_csv(
    df: pd.DataFrame, item_id: int, item_name: str, realm: str = "ambershire"
):
    """Save DataFrame to a CSV file."""
    output_dir = Path("data/market_data") / realm
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_dir / f"item_{item_id}_{item_name}_last_30d.csv"
    df.to_csv(file_name)
    console.print(f"Data saved to [green]{file_name}[/green]")


def main():
    items_path = Path("data/items.json")
    with items_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        items = data["items"]  # Access the nested items dictionary

    console.print(
        f"[bold cyan]📦 Fetching auction data for {len(items)} items...[/bold cyan]"
    )

    for item_id, item_name in items.items():
        file_path = (
            Path("data/market_data/ambershire")
            / f"item_{item_id}_{item_name}_last_30d.csv"
        )
        if is_recent(file_path, hours=24):
            console.print(
                f"[yellow]⏭️ Skipping item ID {item_id} - {item_name} (data is recent)[/yellow]"
            )
            continue

        try:
            console.print(
                f"\n[bold]🔍 Fetching data for item ID {item_id} - {item_name}[/bold]"
            )
            console.print(item_id)
            data = fetch_auction_history(item_id)
            df = to_dataframe(data)
            save_to_csv(df, item_id, item_name)
        except Exception as e:
            console.print(
                f"[red]❌ Failed to fetch data for item ID {item_id}: {e}[/red]"
            )


if __name__ == "__main__":
    main()
