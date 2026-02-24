# GitHub Copilot Instructions for Goblinomincs

## Project Purpose

Goblinomincs is a Python 3.10+ project (managed with **uv**) that analyzes World of Warcraft Classic auction house data to uncover gold-making opportunities. The tool ingests **local CSV/JSON data** (items, vendor items, recipes, and hourly market history) and produces:

- 30-day market summaries with weekly patterns
- Real-time “buy/sell now” signals by comparing prices to 3-day averages
- Crafting profitability reports with current vs 7-day average costs

Future roadmap includes optional **local LLM (Ollama)** integrations for natural-language insights.

## Code Style & Design

- Follow **PEP 8** and add **type hints** when practical.
- Prefer small, composable functions over monoliths.
- Use **`pathlib`** for file paths.
- Use **`pandas`** for data manipulation and time-series work.
- Use **`rich`** for terminal tables, prompts, and panels (interactive CLI lives in `cli.py`).
- All scripts should remain runnable via **uv** (`uv run …`).
- ALWAYS use descriptive variable/function names and add docstrings for public functions.

## Key Modules & Data

- `analyze_market_data.py` – daily/hourly analysis, buy/sell signals, craft summaries.
- `market_data.py` – loads CSV market snapshots into a combined DataFrame (converts copper→gold).
- `recipe_analysis.py` – computes crafting costs, 7-day averages, and profit metrics.
- `vendor_items.py` – fixed-price vendor item lookups (e.g., Crystal Vial).
- `cli.py` – interactive Rich-based menu for market summary, opportunities, and crafts.
- `data/items.json` – tracked auction items (string IDs → item names).
- `data/vendor_items.json` – vendor-priced items with gold values.
- `data/recipes.json` – crafting recipes with reagent breakdowns.
- `data/market_data/ambershire/*.csv` – hourly market history (timestamp, bid, min_buy, avg_price, available).
- `tests/` – pytest suite covering loaders and analysis helpers.

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

## Copilot Guidance

When generating code or suggestions:

- Keep changes focused; explain rationale briefly.
- Reuse existing pandas idioms (boolean masks, `.loc`, rolling averages).
- Align with current analysis conventions:
  - 30-day overall mean, 7-day rolling windows for trends.
  - 3-day average comparisons for buy/sell alerts.
  - Profit outputs in absolute gold **and** percentages when relevant.
- Respect the Rich-based output style (tables, color-coded cells, readable headings).
- For new features, prefer extending current modules (`analyze_market_data.py`, `recipe_analysis.py`, etc.) instead of creating new parallel flows.
- Encourage structured return values (dicts/lists) that feed into tabular display.
- When touching data paths, rely on `Path` and keep everything workspace-relative.
- For tests, add **pytest** cases under `tests/` and rely on fixtures/helpers where useful.

## Quality Assurance Workflow

**After making any code changes, always perform these steps in order:**

1. **Run pytest** to verify all tests pass:
   ```bash
   uv run pytest -v
   ```
   - All 40 tests must pass (100% success rate required)
   - Check for any test failures or errors
   - Use `uv run pytest -m unit` for faster feedback during development

2. **Run ruff** to check code quality:
   ```bash
   uv run ruff check .
   ```
   - Fix any linting errors before proceeding
   - Use `uv run ruff check --fix .` for auto-fixable issues
   - Ensure zero errors before committing

3. **Update README.md** if needed:
   - Check if changes affect user-facing features, commands, or configuration
   - Run `uv run ruff check README.md` to verify formatting


## CLI Expectations

- The interactive menu is in `cli.py` and already wired to load data once per session.
- If adding new menu options, follow the current Rich panel + prompt pattern.
- No Typer commands are currently exposed; keep CLI lightweight unless requirements change.

## Don’ts

- Don’t introduce heavy web frameworks or GUIs—this remains a CLI/data tool.
- Don’t assume external network access unless explicitly requested.
- Don’t hardcode absolute paths or server-specific details; keep Ambershire as default unless instructed.
- Don’t duplicate logic already encapsulated in `market_data.py` or `recipe_analysis.py`.
