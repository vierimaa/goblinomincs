# Goblinomincs

A Python-based World of Warcraft Classic auction house analysis tool that helps identify gold-making opportunities through market data analysis, crafting profitability calculations, and trading timing recommendations.

## Features

### 📊 Market Analysis
- **30-Day Market Summary**: Track average prices, trends, and weekly patterns
- **Daily Pattern Analysis**: Identify best days to buy and sell each item
- **Price Trend Tracking**: Compare 7-day vs 30-day averages to spot trends

### 💰 Trading Opportunities
- **Buy/Sell Now Alerts**: Identifies items cheaper/expensive compared to 3-day averages
- **Price Deviation Detection**: Highlights 5%+ price swings for immediate action
- **Gold Profit Calculations**: Shows actual gold profit potential, not just percentages

### ⚗️ Crafting Profitability
- **Recipe Analysis**: Calculate profit margins for 11+ alchemy recipes
- **Current vs Weekly Averages**: Compare current costs to 7-day averages for timing decisions
- **Vendor Item Support**: Handles fixed-price vendor materials (Crystal Vial)
- **Material Cost Breakdown**: See individual reagent costs and total crafting expenses

### 🎨 Interactive CLI
- **Menu-Driven Interface**: Easy navigation through analysis views
- **Rich Terminal Output**: Color-coded tables with visual indicators
- **Customizable Filters**: Adjust minimum profit thresholds on-the-fly

## Requirements

- Python 3.10+
- uv for Python and dependency management
- Market data from wow-auctions.net (Ambershire server)

## Installation

1. Install uv (if not already installed):
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/goblinomincs.git
cd goblinomincs
```

3. Install Python and dependencies:
```bash
uv python install 3.12
uv sync
```

## Usage

### First Time Setup: Fetch Market Data
Before running the CLI, you need to download market data from wow-auctions.net:
```bash
uv run fetch-auction-data
```

This populates `data/market_data/ambershire/` with hourly price snapshots for the past 30 days.

### Interactive CLI (Recommended)
Launch the interactive menu to explore all analysis views:
```bash
uv run goblinomincs
```

**Menu Options:**
1. **Market Summary** - 30-day overview with trends and flip profits
2. **Buy/Sell Opportunities** - Immediate trading recommendations
3. **Profitable Crafts** - Recipe profitability with cost breakdowns
4. **Show All Views** - Complete analysis at once
5. **Exit**

### Direct Analysis Scripts

**Fetch Latest Market Data:**
```bash
uv run fetch-auction-data
```

**Run Full Analysis:**
```bash
uv run python -m goblinomincs.analyze_market_data
```

## Project Structure

```
goblinomincs/
├── src/
│   └── goblinomincs/           # Main package
│       ├── __init__.py
│       ├── analyze_market_data.py  # Market analysis functions
│       ├── cli.py                  # Interactive menu interface
│       ├── fetch_auction_data.py   # Data collection from API
│       ├── market_data.py          # Data loading utilities
│       ├── recipe_analysis.py      # Crafting profitability
│       └── vendor_items.py         # Vendor item handling
├── data/
│   ├── items.json              # Tracked item definitions (52 items)
│   ├── recipes.json            # Crafting recipes (11 alchemy recipes)
│   ├── vendor_items.json       # Fixed-price vendor items
│   └── market_data/
│       └── ambershire/         # Hourly price data (CSV files)
├── tests/                      # Pytest test suite
│   ├── test_market_data.py
│   ├── test_vendor_items.py
│   └── test_analyze_market_data.py
├── pyproject.toml              # Project dependencies (PEP 621)
└── pytest.ini                  # Test configuration
```

## Key Modules

### `goblinomincs.cli`
Interactive menu system using Rich library for beautiful terminal UI. Loads data once and allows exploring different analysis views without reloading.

### `goblinomincs.analyze_market_data`
Core analysis functions:
- `analyze_daily_patterns()` - Day-of-week price analysis
- `analyze_buy_sell_now()` - Compare current prices to 3-day averages
- `show_buy_sell_now_opportunities()` - Display buy/sell tables
- `show_profitable_crafts()` - Display recipe profitability

### `goblinomincs.recipe_analysis`
Crafting economics:
- `calculate_crafting_cost()` - Compute current and 7-day average costs/profits
- `get_profitable_recipes()` - Return sorted list of profitable recipes

### `goblinomincs.vendor_items`
Handle items with fixed vendor prices (e.g., Crystal Vial at 0.2g).

## Development

### Setup Development Environment

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python and dependencies (including dev tools)
uv python install 3.12
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov
```

### Running Tests

The project includes pytest tests for core functionality:
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_market_data.py

# Verbose output
uv run pytest -v
```

### Adding New Items

Edit `data/items.json` to track additional items:
```json
{
  "items": {
    "12345": "Item Name"
  }
}
```

### Adding New Recipes

Edit `data/recipes.json` to analyze new crafting recipes:
```json
{
  "recipes": [
    {
      "id": 12345,
      "source": "Alchemy",
      "name": "Recipe Name",
      "reagents": [
        { "id": 1234, "name": "Reagent", "quantity": 2 }
      ]
    }
  ]
}
```

## Data Sources

Market data is fetched from [wow-auctions.net](https://wow-auctions.net) API for the Ambershire server (WoW Classic Era). Data includes:
- Hourly snapshots over 30 days
- Bid prices, minimum buyout, average prices
- Available quantity on auction house

## Future Enhancements

- 🤖 Local LLM integration (Ollama) for natural language market queries
- 📈 Price prediction using time-series forecasting
- 🚨 Anomaly detection for unusual market events
- 📊 Visual charts and graphs with matplotlib/plotly
- 💾 Trade logging and profit tracking
- ⏰ Time-of-day pattern analysis (hourly best times)
- 🌐 Multi-server support

## License

MIT