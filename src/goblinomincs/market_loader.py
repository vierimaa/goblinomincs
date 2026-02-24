"""Loads per-item CSV market history files into a combined DataFrame."""

import warnings
from pathlib import Path

import pandas as pd

from goblinomincs.json_loader import load_json_data

DATA_DIR = Path("data/market_data/ambershire")
ITEMS_FILE = Path("data/items.json")


def load_items(items_file: Path | None = None) -> dict:
    """Load the raw items mapping from items.json.

    Returns the raw mapping of item_id -> {"name": ..., "category": ...}.

    Args:
        items_file: Optional path to items.json file (uses default if None)

    Returns:
        dict: Dictionary mapping item IDs to item info dicts
    """
    file_path = items_file or ITEMS_FILE
    return load_json_data(file_path, key="items")


def load_all_market_data(data_dir: Path | None = None, items_file: Path | None = None) -> pd.DataFrame:
    """Combine all CSVs in the market data folder into one DataFrame.

    Args:
        data_dir: Optional path to market data directory (uses default if None)
        items_file: Optional path to items.json file (uses default if None)

    Returns:
        pd.DataFrame: Combined market data with copper values converted to gold

    Raises:
        FileNotFoundError: If no valid market data files are found
    """
    all_data = []
    market_dir = data_dir or DATA_DIR
    items_map = load_items(items_file)

    for item_id, item_info in items_map.items():
        item_name = item_info["name"]
        csv_path = market_dir / f"item_{item_id}_{item_name}_last_30d.csv"
        if not csv_path.exists():
            warnings.warn(
                f"Missing data file for {item_name} (ID {item_id})",
                UserWarning,
                stacklevel=2,
            )
            continue

        try:
            df = pd.read_csv(
                csv_path,
                names=["timestamp", "bid", "min_buy", "avg_price", "available"],
                header=0,  # First row contains headers
                index_col="timestamp",
                parse_dates=True,
            )
        except Exception as e:
            warnings.warn(
                f"Error loading {item_name} (ID {item_id}): {e}",
                UserWarning,
                stacklevel=2,
            )
            continue

        # Validate expected columns
        if not all(col in df.columns for col in ["bid", "min_buy", "avg_price"]):
            warnings.warn(
                f"{item_name} missing expected columns. Has: {df.columns.tolist()}",
                UserWarning,
                stacklevel=2,
            )
            continue

        # Convert copper to gold (divide by 10000, as 1 gold = 10000 copper)
        price_columns = ["bid", "min_buy", "avg_price"]
        df[price_columns] = df[price_columns].div(10000)

        # Add weekday and item metadata columns
        df["weekday"] = df.index.day_name()
        df["item_name"] = item_name
        df["item_id"] = item_id

        all_data.append(df)

    if not all_data:
        raise FileNotFoundError("No valid market data files were found.")

    return pd.concat(all_data)
