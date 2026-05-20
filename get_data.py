import pandas as pd
from fredapi import Fred
import os
import yfinance as yf
from dotenv import load_dotenv
from utils import start_date

load_dotenv()

def filepath(filename, base_dir=os.path.join(".", "data")):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, f"{filename}.csv")

def get_spy_data():
    """Download monthly SPY closing prices from Yahoo Finance and save to data/SPY.csv."""
    tempdf = yf.download('SPY', start=start_date, interval="1mo")[('Close', 'SPY')]
    tempdf.name = 'SPY'
    data_to_csv(tempdf, 'SPY')

def get_fred_data(api_key, series_ids):
    fred = Fred(api_key = api_key)
    for id in series_ids:
        data = fred.get_series(id)
        df = pd.DataFrame(data, columns = [id])
        df.index.name = 'Date'
        data_to_csv(df, id)

def data_to_csv(data, filename):
    filename = filepath(filename)
    print(f"Writing data to {filename}")
    data.to_csv(filename, sep=',', index=True, encoding='utf-8')


if __name__ == '__main__':
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        raise ValueError("FRED_API_KEY not set. Add it to a .env file or export it as an environment variable.")
    ids = ['DGS3MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'FEDFUNDS', 'CPILFESL', 'UNRATE']
    get_fred_data(api_key, ids)
    get_spy_data()




