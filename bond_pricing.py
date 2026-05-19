import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date
import yfinance as yf
from sklearn.preprocessing import StandardScaler

current_date = date.today()

def filepath(filename, base_dir=os.path.join(".", "data")):
    return os.path.join(base_dir, f"{filename}.csv")

def get_current_yields(files):
    plt.figure(1,figsize=(10, 6))
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
    plt.show()
    return current_yields

def price_bond(face_value, coupon_rate, maturities):
    prices = []
    for maturity in maturities:
        discount_rate = np.interp(maturity, current_yields['Maturity'], current_yields['Yield'])/100
        coupon_payment = (face_value * coupon_rate)
        discounted_payments = (coupon_payment / discount_rate) * (1-(1/(1+discount_rate))**maturity)
        discounted_face_value = (face_value / (1+discount_rate)**maturity)
        present_value = discounted_payments + discounted_face_value
        prices.append(present_value)
    return prices

def graph_bonds():
    #Bond parameters
    face_value = 2000  # Face value of the bond
    maturities = np.arange(1, 11)  #Maturity from 1 to 10 years

    #Initial slider data
    initial_coupon_rate = 0.05
    prices = price_bond(face_value, initial_coupon_rate, maturities)

    fig = go.Figure()
    # Add the initial trace
    fig.add_trace(go.Scatter(x=maturities, y=prices, mode='lines', name=f"Coupon Rate"))

    fig.update_layout(
        title="Bond Price vs Maturity",
        xaxis_title="Maturity (Years)",
        yaxis_title="Bond Price",
        showlegend=True,
    )
    steps = []
    coupon_rates = np.linspace(0.01, 0.10, 10)  # Coupon rates from 1% to 10%
    for rate in coupon_rates:
        step = {
            "method": "update",
            "args": [
                {"y": [price_bond(face_value, rate, maturities)]},
            ],
            "label": f"{rate:.2%}",  # Slider label
            "name": f"Coupon Rate"
        }
        steps.append(step)

    fig.update_layout(
        sliders=[
            {
                "active": 4,  # Index of the default value
                "currentvalue": {"prefix": "Coupon Rate: ", "font": {"size": 16}},
                "steps": steps,
                "x": 0.5,
                "y": -0.15,
                "xanchor": "center",
                "yanchor": "top",
            }
        ]
    )
    fig.show()

def yield_curves(files):
    plt.figure(2,figsize=(10, 6))
    for file in files:
        df = pd.read_csv(filepath(file))
        df = df.dropna()
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        start_date = '2014-12-05'
        end_date = current_date
        df = df.loc[start_date:end_date]
        plt.plot(df.index, df[file], label= file)

    # Adding titles and labels
    plt.title("U.S. Treasury Yields Over Time", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Yield (%)", fontsize=14)

    plt.legend()
    plt.grid(True)
    plt.show()

def correlation(files):
    fig, axs = plt.subplots(2, 2, figsize=(15, 12), num = 3)
    measurements = ['UNRATE', 'CPILFESL', 'SPY']
    scaler = StandardScaler()
    corrs = pd.DataFrame(index=measurements, columns=files)
    for i, ax in enumerate(axs.flat):  # axs.flat flattens the 2x2 array into a 1D array
        ax.set_title(files[i])
        df = pd.read_csv(filepath(files[i]))
        df = df.dropna()
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        start_date = '2014-12-05'
        end_date = current_date
        df = df.loc[start_date:end_date]
        df[files[i]] = scaler.fit_transform(df[[files[i]]])
        ax.plot(df.index, df[files[i]], label= files[i])
        ax.set_xlabel('Date')
        ax.set_ylabel('Rate (%)')
        for measurement in measurements:
            data = pd.read_csv(filepath(measurement))
            data = data.dropna()
            data.set_index('Date', inplace=True)
            data.index = pd.to_datetime(data.index)
            start_date = '2014-12-05'
            end_date = current_date
            data = data.loc[start_date:end_date]
            data[measurement] = scaler.fit_transform(data[[measurement]])
            ax.plot(data.index, data[measurement], label= measurement)
            ax.legend(loc='upper left')
            corr = df[files[i]].corr(data[measurement])
            corrs.loc[measurement, files[i]] = corr

    plt.tight_layout()
    plt.show()
    print("Correlation DataFrame:")
    print(corrs)


if __name__ == '__main__':
    file_list = ['DGS1', 'DGS3', 'DGS5', 'DGS7', 'DGS10']
    current_yields = get_current_yields(file_list)
    price_bond(1000, .05, maturities= [4])
    graph_bonds()
    file_list = ['DGS3MO', 'DGS2', 'DGS10', 'FEDFUNDS']
    yield_curves(file_list)
    correlation(file_list)


