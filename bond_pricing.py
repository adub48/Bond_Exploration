import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from scipy.optimize import brentq

current_date = date.today()
start_date = (pd.Timestamp.today() - pd.DateOffset(years=10)).strftime('%Y-%m-%d')

def filepath(filename, base_dir=os.path.join(".", "data")):
    """Return the CSV path for a given FRED series or ticker symbol."""
    return os.path.join(base_dir, f"{filename}.csv")

def get_current_yields(files):
    """Fetch the most recent yield for each maturity, plot the yield curve, and return a DataFrame."""
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

def price_bond(yields, face_value, coupon_rate, maturities):
    """Price a fixed-coupon bond using DCF, interpolating the discount rate from the yield curve."""
    prices = []
    for maturity in maturities:
        discount_rate = np.interp(maturity, yields['Maturity'], yields['Yield'])/100
        coupon_payment = (face_value * coupon_rate)
        discounted_payments = (coupon_payment / discount_rate) * (1-(1/(1+discount_rate))**maturity)
        discounted_face_value = (face_value / (1+discount_rate)**maturity)
        present_value = discounted_payments + discounted_face_value
        prices.append(present_value)
    return prices

def bond_metrics(yields, face_value, coupon_rate, maturity):
    """Return Macaulay duration, modified duration, and convexity for a fixed-coupon bond."""
    r = np.interp(maturity, yields['Maturity'], yields['Yield']) / 100
    coupon = face_value * coupon_rate
    times = np.arange(1, maturity + 1)
    cash_flows = np.full(maturity, coupon, dtype=float)
    cash_flows[-1] += face_value
    discounted = cash_flows / (1 + r) ** times
    price = discounted.sum()
    macaulay_duration = (times * discounted).sum() / price
    modified_duration = macaulay_duration / (1 + r)
    convexity = ((times ** 2 + times) * discounted).sum() / (price * (1 + r) ** 2)
    return {
        'price': price,
        'macaulay_duration': macaulay_duration,
        'modified_duration': modified_duration,
        'convexity': convexity,
    }

def yield_to_maturity(face_value, coupon_rate, maturity, market_price):
    """Solve for the yield that equates the bond's DCF value to its market price."""
    coupon = face_value * coupon_rate
    times = np.arange(1, maturity + 1)
    cash_flows = np.full(maturity, coupon, dtype=float)
    cash_flows[-1] += face_value

    def price_at_yield(r):
        return (cash_flows / (1 + r) ** times).sum() - market_price

    return brentq(price_at_yield, 1e-6, 10.0)

def graph_bonds(yields):
    """Plot bond price vs maturity for a range of coupon rates using an interactive Plotly slider."""
    #Bond parameters
    face_value = 2000  # Face value of the bond
    maturities = np.arange(1, 11)  #Maturity from 1 to 10 years

    #Initial slider data
    initial_coupon_rate = 0.05
    prices = price_bond(yields, face_value, initial_coupon_rate, maturities)

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
                {"y": [price_bond(yields, face_value, rate, maturities)]},
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
    """Plot historical Treasury yields for the given FRED series over the past 10 years."""
    plt.figure(2,figsize=(10, 6))
    for file in files:
        df = pd.read_csv(filepath(file))
        df = df.dropna()
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
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
    """Plot each of 4 yield series against unemployment, CPI, and SPY, and print the correlation matrix."""
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

    face_value, coupon_rate, maturity = 1000, 0.05, 4
    bond_price = price_bond(current_yields, face_value, coupon_rate, maturities=[maturity])[0]
    print(f"Bond price: ${bond_price:,.2f}")

    metrics = bond_metrics(current_yields, face_value, coupon_rate, maturity)
    print(f"Macaulay duration:  {metrics['macaulay_duration']:.4f} years")
    print(f"Modified duration:  {metrics['modified_duration']:.4f}")
    print(f"Convexity:          {metrics['convexity']:.4f}")

    ytm = yield_to_maturity(face_value, coupon_rate, maturity, bond_price)
    print(f"Yield to maturity:  {ytm:.4%}")

    graph_bonds(current_yields)
    file_list = ['DGS3MO', 'DGS2', 'DGS10', 'FEDFUNDS']
    yield_curves(file_list)
    correlation(file_list)


