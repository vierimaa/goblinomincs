import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path("data/market_data/ambershire")
ITEMS_FILE = Path("data/items.json")


def load_item_names():
    """Load item names from items.json."""
    with open("data/items.json", "r") as f:
        items_data = json.load(f)
    return items_data["items"]


def load_all_market_data():
    """Combine all CSVs in the market data folder into one DataFrame."""
    all_data = []
    item_names = load_item_names()

    for item_id, item_name in item_names.items():
        csv_path = DATA_DIR / f"item_{item_id}_{item_name}_last_30d.csv"
        if not csv_path.exists():
            print(f"Warning: Missing data file for {item_name} (ID {item_id})")
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
            print(f"Error loading {item_name} (ID {item_id}): {e}")
            continue

        # Debug: Check what columns we actually have
        if not all(col in df.columns for col in ["bid", "min_buy", "avg_price"]):
            print(f"Warning: {item_name} has columns: {df.columns.tolist()}")
            continue

        # Convert copper to gold (divide by 10000, as 1 gold = 10000 copper)
        price_columns = ["bid", "min_buy", "avg_price"]
        df[price_columns] = df[price_columns].div(10000)

        # Add weekday information
        df["weekday"] = df.index.day_name()
        df["item_name"] = item_name
        df["item_id"] = item_id

        all_data.append(df)

        if not all_data:
            raise FileNotFoundError("No valid market data files were found.")

    return pd.concat(all_data)
