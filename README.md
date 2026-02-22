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
- **Recipe Analysis**: Calculate profit margins for 13 alchemy recipes
- **Recursive Costing**: Smart cost calculation that compares crafting vs buying reagents
- **Current vs Weekly Averages**: Compare current costs to 7-day averages for timing decisions
- **Vendor Item Support**: Handles fixed-price vendor materials (Crystal Vial, Leaded Vial)
- **Material Cost Breakdown**: See individual reagent costs, sources (vendor/crafted/auction), and total crafting expenses
- **Recipes by Profession**: View all recipes organized by source with cost analysis

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
4. **Recipes by Profession** - All recipes organized by source (Alchemy)
5. **Show All Views** - Complete analysis at once
6. **Exit**

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
│       ├── analyze_market_data.py  # Market analysis (calculation + presentation)
│       ├── cli.py                  # Interactive menu interface
│       ├── data_loaders.py         # Common JSON loading utilities
│       ├── fetch_auction_data.py   # Data collection from API
│       ├── market_data.py          # Data loading utilities
│       ├── recipe_analysis.py      # Crafting profitability
│       └── vendor_items.py         # Vendor item handling
├── data/
│   ├── items.json              # Tracked item definitions (63 items)
│   ├── recipes.json            # Crafting recipes (13 alchemy recipes)
│   ├── vendor_items.json       # Fixed-price vendor items (Crystal Vial, Leaded Vial)
│   └── market_data/
│       └── ambershire/         # Hourly price data (CSV files)
├── tests/                      # Pytest test suite (40 tests)
│   ├── conftest.py             # Shared fixtures and test utilities
│   ├── test_analyze_market_data.py
│   ├── test_data_loaders.py    # Common data loader tests
│   ├── test_market_data.py
│   ├── test_recipe_analysis.py # Recursive costing and recipe tests
│   └── test_vendor_items.py
├── pyproject.toml              # Project dependencies (PEP 621)
└── pytest.ini                  # Test configuration
```


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

The project includes 40 pytest tests covering core functionality with 100% pass rate:

```bash
# Run all tests with coverage
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_recipe_analysis.py

# Run only unit tests (30 tests)
uv run pytest -m unit

# Run only integration tests (10 tests)
uv run pytest -m integration

# Skip coverage for faster execution
uv run pytest --no-cov

# Generate HTML coverage report
uv run pytest --cov-report=html
```

### Code Quality

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

**Ruff Configuration** (in `pyproject.toml`):
- Line length: 88 (Black-compatible)
- Target: Python 3.10+
- Enabled rules: PEP 8, import sorting, type hints, pathlib usage, code simplifications
- Replaces: flake8, black, isort, pyupgrade

**Code Quality Standards:**
- ✅ All code formatted with Ruff
- ✅ Zero linting errors
- ✅ Type hints on public APIs
- ✅ Comprehensive docstrings
- ✅ Single Responsibility Principle applied
- ✅ Separation of calculation from presentation
- ✅ DRY (Don't Repeat Yourself) throughout

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


## License

MIT