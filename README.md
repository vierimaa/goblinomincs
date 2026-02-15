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

## Architecture & Design Patterns

Goblinomincs follows Python best practices and design patterns for maintainability and testability:

### Separation of Concerns
- **Calculation functions** return data structures (dicts, lists)
- **Display functions** handle presentation (Rich tables, console output)
- **Data loading** centralized in dedicated modules

### Single Responsibility Principle
Each module has a clear, focused purpose:
- `data_loaders.py` - Generic JSON file loading
- `market_data.py` - CSV market data loading and transformation
- `recipe_analysis.py` - Crafting cost calculations
- `analyze_market_data.py` - Market analysis computations
- `cli.py` - User interface and menu navigation

### Dependency Injection
Functions accept optional parameters for testability:
```python
def load_item_names(items_file: Path | None = None) -> dict:
    """Uses default path if not provided"""
    
def show_profitable_crafts(df, min_profit_pct=5, console_inst=None):
    """Uses module console if not provided"""
```

### Error Handling
- Library functions raise exceptions for calling code to handle
- Warning system for non-critical issues (missing data files)
- User-facing CLI catches and displays errors gracefully

## Key Modules

### `goblinomincs.cli`
Interactive menu system using Rich library for beautiful terminal UI. Loads data once and allows exploring different analysis views without reloading.
- `build_market_summary_table()` - Reusable table builder (DRY principle)
- `interactive_menu()` - Main menu loop

### `goblinomincs.data_loaders`
Common data loading utilities following the Rule of Three:
- `load_json_data()` - Generic JSON file loader with optional key extraction
- Used by all modules that load JSON configuration files

### `goblinomincs.analyze_market_data`
Core analysis functions separated into calculation and presentation layers:

**Calculation functions (testable, returns data):**
- `analyze_daily_patterns()` - Day-of-week price analysis
- `analyze_buy_sell_now()` - Compare current prices to 3-day averages
- `get_buy_sell_opportunities()` - Find items with significant price deviations
- `get_recipes_by_source()` - Group recipes by profession with cost analysis

**Display functions (presentation layer):**
- `display_buy_sell_opportunities()` - Render buy/sell tables
- `display_profitable_crafts()` - Render recipe profitability table
- `display_recipes_by_source()` - Render profession-organized tables

**Wrapper functions (convenience):**
- `show_buy_sell_now_opportunities()` - Combines calculation + display
- `show_profitable_crafts()` - Combines calculation + display
- `show_recipes_by_source()` - Combines calculation + display

### `goblinomincs.recipe_analysis`
Crafting economics with recursive costing:
- `calculate_crafting_cost()` - Public API for cost calculation
- `_calculate_crafting_cost_internal()` - Private recursive implementation
- `get_best_reagent_price()` - Smart price selection (vendor/crafted/auction)
- `get_profitable_recipes()` - Return sorted list of profitable recipes
- Supports nested recipes (e.g., Potion of Quickness uses Swiftness Potion)

### `goblinomincs.market_data`
CSV data loading and transformation:
- `load_item_names(items_file=None)` - Load item definitions with optional path
- `load_all_market_data(data_dir=None, items_file=None)` - Combine CSV files into DataFrame
- Configurable paths for testing and flexibility
- Uses Python warnings for non-critical issues

### `goblinomincs.fetch_auction_data`
API data collection with improved error handling:
- `fetch_auction_history()` - HTTP request with proper error handling
- `should_fetch_item()` - Determine if refresh is needed
- `fetch_and_save_item()` - Fetch, transform, and save single item
- `main()` - Orchestrate fetching all items with summary reporting

### `goblinomincs.vendor_items`
Handle items with fixed vendor prices:
- `load_vendor_items(vendor_file=None)` - Load vendor price data
- `get_vendor_price()` - Lookup vendor price by item ID
- Crystal Vial: 0.2g, Leaded Vial: 0.04g

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

**Test Organization:**
- **Unit Tests** (`@pytest.mark.unit`) - Test individual functions in isolation (30 tests)
- **Integration Tests** (`@pytest.mark.integration`) - Test with real data files (10 tests)
- **Fixtures** (`conftest.py`) - Shared test data and utilities
- **Parametrized Tests** - Reduce duplication with `@pytest.mark.parametrize`

**Test Coverage:**
- `test_analyze_market_data.py` - Market analysis calculations (6 tests)
- `test_data_loaders.py` - Common JSON loader with error handling (6 tests)
- `test_market_data.py` - Data loading and transformation (3 tests)
- `test_recipe_analysis.py` - Crafting cost calculations, recursive recipes, vendor items (24 tests)
- `test_vendor_items.py` - Vendor price lookups (5 tests, parametrized)

**Coverage Metrics:**
- `data_loaders.py`: 100%
- `vendor_items.py`: 100%
- `recipe_analysis.py`: 97%
- Overall: 40% (presentation layers intentionally excluded)

All tests follow pytest best practices with fixtures, parametrization, markers, and comprehensive coverage reporting. Calculation functions are tested independently from presentation logic.

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

## Recent Improvements (v0.2.0)

### Refactoring & Code Quality
- **Separated Calculation from Presentation**: Analysis functions now return data structures instead of directly printing, making them fully testable
- **Common Data Loader**: Extracted JSON loading pattern (Rule of Three) into `data_loaders.py`
- **Configurable File Paths**: All data loading functions accept optional path parameters for testing flexibility
- **Standardized Error Handling**: Library functions use exceptions, warnings for non-critical issues, graceful CLI error displays
- **Improved fetch_auction_data.py**: Refactored into smaller, focused functions with better error handling and summary reporting
- **Private Function Marking**: Internal functions now use underscore prefix (`_function_name`)
- **DRY Compliance**: Eliminated 100+ lines of duplicated code in CLI table building
- **Dependency Injection**: Console and file paths can be injected for testing

### Testing Improvements (v0.2.1)
- **Pytest Fixtures**: Converted helper functions to reusable fixtures in `conftest.py`
- **Shared Test Data**: Centralized sample data creation (`sample_market_data`, `sample_item_data`) used across test files
- **Parametrized Tests**: Reduced duplication using `@pytest.mark.parametrize` (e.g., vendor price tests)
- **Test Markers**: Organized tests with `unit` and `integration` markers for selective test execution
- **Coverage Reporting**: Integrated `pytest-cov` with automatic coverage reports showing 40% overall (100% on core utilities)
- **Coverage Configuration**: Configured in `pyproject.toml` to exclude tests and generated files
- **Test Count Growth**: Expanded from 28 to 40 tests (+42.9%) with better organization

### Code Quality
- All 40 tests passing with 100% success rate
- Zero Ruff linting errors
- Code formatted with Ruff auto-formatter
- Comprehensive test coverage following pytest best practices
- Tests organized by type (unit vs integration) for faster CI/CD feedback

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