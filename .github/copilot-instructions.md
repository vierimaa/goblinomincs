# GitHub Copilot Instructions for WoW Gold AI App

## Project Purpose

This Python 3.10+ project (managed with **Poetry**) analyzes World of Warcraft auction house data to discover gold-making opportunities.

The app loads **local JSON data** — including item definitions, recipes, and auction market history — and performs analysis to identify trends and opportunities.
It can later integrate with **local LLMs (via Ollama)** for generating insights and answering natural-language questions about the market.

## Code Style & Design

* Follow **PEP 8** and use **type hints** throughout the codebase.
* Prefer **clarity and modularity** over clever shortcuts.
* Use **`pathlib`** for all file and directory handling.
* Use **`pandas`** for data manipulation and statistics.
* Use **`rich`** for structured and colorful CLI output.
* All scripts must be runnable with **Poetry**.

## Key Directories

* `wow_gold_ai/`: main package for CLI commands, AI logic, and utilities.
* `data/items.json`: static metadata for all WoW items of interest.
* `data/market_data/`: contains JSON files with auction history data per item.
* `scripts/`: standalone scripts for data collection and analysis.

  * `market_data.py`: fetches and stores auction data from wow-auctions.net.
  * `analyze_market_data.py`: loads market data, computes averages (30d, 7d), and reports trends.

## Copilot Behavior

When assisting with code generation:

* Suggest small changes at the time, with clear explanations and avoid rewriting large sections.
* Suggest **data fetching**, **processing**, and **storage** utilities compatible with the existing `market_data.py` flow.
* Reuse **pandas-based analysis patterns** as seen in `analyze_market_data.py`.
* Encourage **structured JSON output** for storing or sharing analysis results.
* Suggest helper functions such as:

  * Calculating 30-day and 7-day average prices.
  * Identifying items with positive or negative price trends.
  * Summarizing top movers or profitable crafts.
* For future AI integrations, prefer **LangChain + Ollama** or direct **local inference** setups (no cloud APIs).

## CLI and Script Behavior

* Use **`typer`** for CLI commands.
* Example commands:

  * `update-auctions`: fetch and store new auction data.
  * `analyze-market`: generate summarized market trends.
  * `suggest-opportunities`: use AI to suggest profitable crafts or flips.

## Example Prompts for Copilot Chat

You can ask Copilot things like:

* “Write a helper function to compute average price trends for each item.”
* “Add a Typer command to summarize items with a 7-day price increase.”
* “Load all auction data from data/market_data and return a combined DataFrame.”
* “Integrate an Ollama-powered analysis tool to explain market patterns.”

## Don’t

* Don’t use heavy web frameworks or GUIs — this is a **CLI + data analysis** tool.
* Don’t assume network access unless explicitly fetching data from configured APIs.
* Don’t hardcode paths — always use `pathlib.Path`.

## Notes

* The **`market_data.py`** script is responsible for fetching and saving structured auction data.
* The **`analyze_market_data.py`** script focuses on trend computation and summarization; its logic will later power AI tool integrations.
* Future AI layers should build on existing analysis utilities rather than duplicate logic.
