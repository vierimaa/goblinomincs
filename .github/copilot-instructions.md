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
- For AI extensions, recommend **LangChain + Ollama** or other local-only approaches.

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
   - Update relevant sections (Features, Usage, Project Structure, Recent Improvements)
   - Update test counts if tests were added/removed
   - Update code examples if APIs changed
   - Run `uv run ruff check README.md` to verify formatting

**When to update README.md:**
- New features or commands added
- CLI interface changes
- New dependencies or requirements
- Test suite changes (count, organization, coverage)
- Configuration file changes (pytest.ini, pyproject.toml)
- Breaking changes or deprecations

## CLI Expectations

- The interactive menu is in `cli.py` and already wired to load data once per session.
- If adding new menu options, follow the current Rich panel + prompt pattern.
- No Typer commands are currently exposed; keep CLI lightweight unless requirements change.

## Suggested Enhancements (Roadmap)

- Hour-of-day analysis for optimal trading windows.
- Volatility/risk scores based on rolling standard deviation.
- Supply pressure indicators using the `available` column.
- AH fee-adjusted profit calculations and break-even prices.
- Watchlists, alerts, and export capabilities.

Use these only as inspiration; confirm with the user before building sizable new features.

## Don’ts

- Don’t introduce heavy web frameworks or GUIs—this remains a CLI/data tool.
- Don’t assume external network access unless explicitly requested.
- Don’t hardcode absolute paths or server-specific details; keep Ambershire as default unless instructed.
- Don’t duplicate logic already encapsulated in `market_data.py` or `recipe_analysis.py`.

## Notes

- `fetch_auction_data.py` handles data collection from wow-auctions.net.
- `pytest.ini` configures pytest; run tests via `uv run pytest`.
- Keep vendor item handling centralized in `vendor_items.py` and recipe profit logic in `recipe_analysis.py`.
- Future AI layers should leverage existing analytics instead of recomputing raw statistics.
