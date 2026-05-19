# Bond Pricing Project

Analyzes U.S. Treasury yield curves and prices bonds using real market data from FRED and Yahoo Finance.

## Features

- Plots the current Treasury yield curve
- Prices bonds using discounted cash flow with an interactive coupon rate slider
- Computes Macaulay duration, modified duration, and convexity
- Solves for yield-to-maturity (YTM) given a market price
- Charts historical Treasury yields over the past 10 years
- Correlates yield data against unemployment rate (UNRATE), core CPI (CPILFESL), and SPY
- Exports the correlation matrix to `output/correlations.csv`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your FRED API key:

```bash
cp .env.example .env
# then edit .env and set FRED_API_KEY=your_key_here
```

A free API key can be obtained at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html).

## Usage

**Fetch data** (required once before running analysis):
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
