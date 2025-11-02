import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/market_data/ambershire")


def load_all_market_data():
    """Combine all CSVs in the market data folder into one DataFrame."""
    all_data = []

    for csv_file in DATA_DIR.glob("item_*_last_30d.csv"):
        item_name = csv_file.stem.split("_", 2)[2].replace("_last_30d", "")
        df = pd.read_csv(
            csv_file,
            names=["timestamp", "bid", "min_buy", "avg_price", "available"],
            header=0,  # First row contains headers
            index_col="timestamp",
            parse_dates=True,
        )
        df["item_name"] = item_name
        all_data.append(df)

    return pd.concat(all_data)
