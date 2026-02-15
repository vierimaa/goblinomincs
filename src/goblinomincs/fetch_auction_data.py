from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from rich.console import Console

from goblinomincs.data_loaders import load_json_data

console = Console()


def fetch_auction_history(
    item_id: int, realm: str = "ambershire", period: str = "30d"
) -> dict:
    """Fetch auction history for a specific item from wowauctions.net.

    Args:
        item_id: The WoW item ID
        realm: The realm name (default: "ambershire")
        period: Time period for data (default: "30d")

    Returns:
        dict: JSON response from the API

    Raises:
        requests.HTTPError: If the API request fails
    """
    url = f"https://api.wowauctions.net/items/stats/{period}/{realm}/mergedAh/{item_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def is_recent(file_path: Path, hours: int = 4) -> bool:
    """Check if the file was modified within the last `hours` hours.

    Args:
        file_path: Path to the file to check
        hours: Number of hours to consider as "recent" (default: 4)

    Returns:
        bool: True if file exists and was modified within the specified hours
    """
    if not file_path.exists():
        return False
    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.now() - modified_time < timedelta(hours=hours)


def to_dataframe(data: dict) -> pd.DataFrame:
    """Convert API response to a Pandas DataFrame with proper datetime index.

    Args:
        data: Dictionary of auction data from the API

    Returns:
        pd.DataFrame: DataFrame with datetime index and sorted by date
    """
    df = pd.DataFrame.from_dict(data, orient="index")
    df.index = pd.to_datetime(df.index, format="%Y,%m,%d,%H")
    df.sort_index(inplace=True)
    return df


def save_to_csv(
    df: pd.DataFrame,
    item_id: int,
    item_name: str,
    realm: str = "ambershire",
    output_base: Path | None = None,
) -> Path:
    """Save DataFrame to a CSV file.

    Args:
        df: DataFrame to save
        item_id: The WoW item ID
        item_name: The item name
        realm: The realm name (default: "ambershire")
        output_base: Base directory for output (default: "data/market_data")

    Returns:
        Path: Path to the saved file
    """
    base_dir = output_base or Path("data/market_data")
    output_dir = base_dir / realm
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"item_{item_id}_{item_name}_last_30d.csv"
    df.to_csv(file_path)
    return file_path


def should_fetch_item(
    item_id: str, item_name: str, realm: str = "ambershire", hours: int = 4
) -> bool:
    """Determine if item data needs refreshing.

    Args:
        item_id: The WoW item ID
        item_name: The item name
        realm: The realm name (default: "ambershire")
        hours: Number of hours to consider data as "recent" (default: 4)

    Returns:
        bool: True if data should be fetched, False if recent data exists
    """
    file_path = (
        Path("data/market_data") / realm / f"item_{item_id}_{item_name}_last_30d.csv"
    )
    return not is_recent(file_path, hours)


def fetch_and_save_item(
    item_id: int,
    item_name: str,
    realm: str = "ambershire",
    console_inst: Console | None = None,
) -> bool:
    """Fetch and save data for a single item.

    Args:
        item_id: The WoW item ID
        item_name: The item name
        realm: The realm name (default: "ambershire")
        console_inst: Optional Console instance (uses module console if None)

    Returns:
        bool: True on success, False on failure
    """
    con = console_inst or console

    try:
        con.print(
            f"\n[bold]🔍 Fetching data for item ID {item_id} - {item_name}[/bold]"
        )
        data = fetch_auction_history(item_id, realm)
        df = to_dataframe(data)
        file_path = save_to_csv(df, item_id, item_name, realm)
        con.print(f"Data saved to [green]{file_path}[/green]")
        return True
    except requests.HTTPError as e:
        con.print(f"[red]❌ HTTP error for item ID {item_id}: {e}[/red]")
        return False
    except Exception as e:
        con.print(f"[red]❌ Failed to fetch data for item ID {item_id}: {e}[/red]")
        return False


def main(
    items_file: Path | None = None,
    realm: str = "ambershire",
    refresh_hours: int = 4,
) -> None:
    """Fetch auction data for all tracked items.

    Args:
        items_file: Optional path to items.json (uses default if None)
        realm: The realm name (default: "ambershire")
        refresh_hours: Only fetch if data is older than this many hours (default: 4)
    """
    items_path = items_file or Path("data/items.json")
    items = load_json_data(items_path, key="items")

    console.print(
        f"[bold cyan]📦 Fetching auction data for {len(items)} items...[/bold cyan]"
    )

    success_count = 0
    skipped_count = 0
    failed_count = 0

    for item_id, item_name in items.items():
        if not should_fetch_item(item_id, item_name, realm, refresh_hours):
            console.print(
                f"[yellow]⏭️ Skipping item ID {item_id} - {item_name} (data is recent)[/yellow]"
            )
            skipped_count += 1
            continue

        if fetch_and_save_item(int(item_id), item_name, realm):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  ✅ Successfully fetched: {success_count}")
    console.print(f"  ⏭️ Skipped (recent): {skipped_count}")
    console.print(f"  ❌ Failed: {failed_count}")


if __name__ == "__main__":
    main()
