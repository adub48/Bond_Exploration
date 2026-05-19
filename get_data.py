import pandas as pd
from fredapi import Fred
import os
import yfinance as yf

def filepath(filename, base_dir=os.path.join(".", "data")):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, f"{filename}.csv")

def getSPYdata():
    tempdf = yf.download('SPY', interval="1mo")
    tempdf = tempdf['Adj Close']
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
    # Requested from FRED website
    api_key = '65c759ce023209f366fb4ae5db10160a'
    ids = ['DGS3MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'FEDFUNDS', 'CPILFESL', 'UNRATE']
    get_fred_data(api_key, ids)
    getSPYdata()




