import os
import pandas as pd
from datetime import date

current_date = date.today()
start_date = (pd.Timestamp.today() - pd.DateOffset(years=10)).strftime('%Y-%m-%d')

def filepath(filename, base_dir=os.path.join(".", "data")):
    """Return the CSV path for a given FRED series or ticker symbol."""
    return os.path.join(base_dir, f"{filename}.csv")
