# Bond Pricing Project

Analyzes U.S. Treasury yield curves and prices bonds using real market data from FRED and Yahoo Finance.

## Features

- Plots the current Treasury yield curve
- Prices bonds using discounted cash flow with an interactive coupon rate slider
- Charts historical Treasury yields over time
- Correlates yield data against unemployment rate (UNRATE), core CPI (CPILFESL), and SPY

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pandas matplotlib plotly yfinance scikit-learn fredapi
```

## Usage

**Fetch data** (requires a FRED API key):
```bash
python get_data.py
```

**Run analysis:**
```bash
python bond_pricing.py
```

## Data

Data is pulled from:
- [FRED](https://fred.stlouisfed.org/) — Treasury yields, Fed Funds rate, CPI, unemployment
- Yahoo Finance — SPY monthly prices

CSV files are saved to the `data/` directory.
