# Goblinomincs

A Python-based World of Warcraft auction house analysis tool that helps identify gold-making opportunities using market data and AI-powered insights.

## Features

- Fetch and analyze auction house data from wow-auctions.net
- Track price trends and market patterns
- Identify profitable opportunities
- CLI interface for easy interaction
- Local LLM integration for market insights (planned)

## Requirements

- Python 3.10+
- Poetry for dependency management
- Ollama for local LLM analysis (planned feature)

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

### Fetch Market Data
```bash
poetry run python fetch_auction_data.py
```

### Analyze Market Trends
```bash
poetry run python analyze_market_data.py
```

## Project Structure

```
goblinomincs/
├── data/
│   ├── items.json       # Item definitions
│   ├── recipes.json     # Crafting recipes
│   └── market_data/     # Auction history data
├── fetch_auction_data.py    # Data collection
├── analyze_market_data.py   # Market analysis
└── market_data.py          # Data loading utilities
```

## Development

This project uses Poetry for dependency management. To set up a development environment:

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

## License

MIT