import numpy as np
from scipy.optimize import brentq

def price_bond(yields, face_value, coupon_rate, maturities):
    """Price a fixed-coupon bond using DCF, interpolating the discount rate from the yield curve."""
    prices = []
    for maturity in maturities:
        discount_rate = np.interp(maturity, yields['Maturity'], yields['Yield']) / 100
        coupon_payment = face_value * coupon_rate
        discounted_payments = (coupon_payment / discount_rate) * (1 - (1 / (1 + discount_rate)) ** maturity)
        discounted_face_value = face_value / (1 + discount_rate) ** maturity
        prices.append(discounted_payments + discounted_face_value)
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
