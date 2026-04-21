# Drawdown Probability Analysis

This script simulates a financial timeseries using arithmetic Brownian motion and calculates the historical probability that a specific percentage drawdown from an all-time high is the "bottom" before the price recovers and never drops to that level again.

## Features

- Simulates a daily price series based on an arithmetic formula: `Price[t] = Price[t-1]*(1 + drift + random_noise)`.
- Calculates daily all-time highs (ATH) and percentage drawdowns (rounded to 1 decimal place).
- Calculates the probability of a drawdown being the lowest point before recovery (i.e. all future drawdowns are strictly less severe).
- Outputs a formatted table of occurrences and probabilities grouped by rounded drawdown values.

## Requirements

The script requires `numpy`, `pandas`, and `tabulate`.
If not installed, you can install them via:
```bash
pip install numpy pandas tabulate
```

## Usage

You can run the script with its default parameters (5000 days, $100 initial price, 0.1 drift, 20% volatility) by simply executing:

```bash
python drawdown_analysis.py
```

### CLI Options

You can customize the simulation parameters using the following flags:

- `--days`: Number of days to simulate (default: 5000).
- `--initial-price`: Initial price on day 0 (default: 100.0).
- `--drift`: Average Annual drift (default: 0.1).
- `--volatility`: Annualized volatility (default: 0.20).

### Example

Simulate a 1000-day series starting at $50, with a 0.10 annual drift and 15% annualized volatility:

```bash
python drawdown_analysis.py --days 1000 --initial-price 50.0 --drift 0.1 --volatility 0.15
```
