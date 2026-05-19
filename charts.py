import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler

from utils import filepath, current_date, start_date
from pricing import price_bond

def get_current_yields(files):
    """Fetch the most recent yield for each maturity, plot the yield curve, and return a DataFrame."""
    plt.figure(1, figsize=(10, 6))
    current_yields = {
        file[3:]: pd.read_csv(filepath(file))[file].iloc[-1]
        for file in files
    }
    current_yields = pd.DataFrame(list(current_yields.items()), columns=['Maturity', 'Yield'])
    plt.plot(current_yields['Maturity'], current_yields['Yield'], marker='o')
    plt.title('Yield Curve')
    plt.xlabel('Maturity')
    plt.ylabel('Yield (%)')
    plt.grid()
    return current_yields

def graph_bonds(yields):
    """Plot bond price vs maturity for a range of coupon rates using an interactive Plotly slider."""
    face_value = 2000
    maturities = np.arange(1, 11)
    initial_coupon_rate = 0.05
    prices = price_bond(yields, face_value, initial_coupon_rate, maturities)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=maturities, y=prices, mode='lines', name="Coupon Rate"))
    fig.update_layout(
        title="Bond Price vs Maturity",
        xaxis_title="Maturity (Years)",
        yaxis_title="Bond Price",
        showlegend=True,
    )

    steps = []
    for rate in np.linspace(0.01, 0.10, 10):
        steps.append({
            "method": "update",
            "args": [{"y": [price_bond(yields, face_value, rate, maturities)]}],
            "label": f"{rate:.2%}",
            "name": "Coupon Rate",
        })

    fig.update_layout(sliders=[{
        "active": 4,
        "currentvalue": {"prefix": "Coupon Rate: ", "font": {"size": 16}},
        "steps": steps,
        "x": 0.5,
        "y": -0.15,
        "xanchor": "center",
        "yanchor": "top",
    }])
    fig.show()

def yield_curves(files):
    """Plot historical Treasury yields for the given FRED series over the past 10 years."""
    plt.figure(2, figsize=(10, 6))
    for file in files:
        df = pd.read_csv(filepath(file))
        df = df.dropna()
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        df = df.loc[start_date:current_date]
        plt.plot(df.index, df[file], label=file)

    plt.title("U.S. Treasury Yields Over Time", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Yield (%)", fontsize=14)
    plt.legend()
    plt.grid(True)

def correlation(files):
    """Plot each of 4 yield series against unemployment, CPI, and SPY, and print the correlation matrix."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 12), num=3)
    measurements = ['UNRATE', 'CPILFESL', 'SPY']
    scaler = StandardScaler()
    corrs = pd.DataFrame(index=measurements, columns=files)

    for i, ax in enumerate(axs.flat):
        ax.set_title(files[i])
        df = pd.read_csv(filepath(files[i]))
        df = df.dropna()
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        df = df.loc[start_date:current_date]
        df[files[i]] = scaler.fit_transform(df[[files[i]]])
        ax.plot(df.index, df[files[i]], label=files[i])
        ax.set_xlabel('Date')
        ax.set_ylabel('Z-Score')

        for measurement in measurements:
            data = pd.read_csv(filepath(measurement))
            data = data.dropna()
            data.set_index('Date', inplace=True)
            data.index = pd.to_datetime(data.index)
            data = data.loc[start_date:current_date]
            data[measurement] = scaler.fit_transform(data[[measurement]])
            ax.plot(data.index, data[measurement], label=measurement)
            ax.legend(loc='upper left')
            corrs.loc[measurement, files[i]] = df[files[i]].corr(data[measurement])

    plt.tight_layout(h_pad=4.0)
    print("Correlation DataFrame:")
    print(corrs)
    os.makedirs("output", exist_ok=True)
    corrs.to_csv(os.path.join("output", "correlations.csv"))
