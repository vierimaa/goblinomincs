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
- Poetry for dependency management
- Market data from wow-auctions.net (Ambershire server)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/goblinomincs.git
cd goblinomincs
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

### Interactive CLI (Recommended)
Launch the interactive menu to explore all analysis views:
```bash
poetry run python cli.py
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
poetry run python fetch_auction_data.py
```

**Run Full Analysis:**
```bash
poetry run python analyze_market_data.py
```

## Project Structure

```
goblinomincs/
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
├── cli.py                      # Interactive menu interface
├── fetch_auction_data.py       # Data collection from API
├── analyze_market_data.py      # Market analysis functions
├── market_data.py              # Data loading utilities
├── recipe_analysis.py          # Crafting profitability calculations
├── vendor_items.py             # Vendor item handling
├── pyproject.toml              # Poetry dependencies
└── pytest.ini                  # Test configuration
```

## Key Modules

### `cli.py`
Interactive menu system using Rich library for beautiful terminal UI. Loads data once and allows exploring different analysis views without reloading.

### `analyze_market_data.py`
Core analysis functions:
- `analyze_daily_patterns()` - Day-of-week price analysis
- `analyze_buy_sell_now()` - Compare current prices to 3-day averages
- `show_buy_sell_now_opportunities()` - Display buy/sell tables
- `show_profitable_crafts()` - Display recipe profitability

### `recipe_analysis.py`
Crafting economics:
- `calculate_crafting_cost()` - Compute current and 7-day average costs/profits
- `get_profitable_recipes()` - Return sorted list of profitable recipes

### `vendor_items.py`
Handle items with fixed vendor prices (e.g., Crystal Vial at 0.2g).

## Development

### Setup Development Environment

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies (including dev tools)
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov
```

### Running Tests

The project includes pytest tests for core functionality:
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_market_data.py

# Verbose output
poetry run pytest -v
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