import matplotlib.pyplot as plt

from charts import get_current_yields, graph_bonds, yield_curves, correlation
from pricing import price_bond, bond_metrics, yield_to_maturity

# --- Yield curve ---
yield_file_list = ['DGS1', 'DGS3', 'DGS5', 'DGS7', 'DGS10']
current_yields = get_current_yields(yield_file_list)

# --- Bond pricing and risk metrics ---
face_value, coupon_rate, maturity = 1000, 0.05, 4
bond_price = price_bond(current_yields, face_value, coupon_rate, maturities=[maturity])[0]
print(f"Bond price:         ${bond_price:,.2f}")

metrics = bond_metrics(current_yields, face_value, coupon_rate, maturity)
print(f"Macaulay duration:  {metrics['macaulay_duration']:.4f} years")
print(f"Modified duration:  {metrics['modified_duration']:.4f}")
print(f"Convexity:          {metrics['convexity']:.4f}")

ytm = yield_to_maturity(face_value, coupon_rate, maturity, bond_price)
print(f"Yield to maturity:  {ytm:.4%}")

# --- Interactive bond price chart ---
graph_bonds(current_yields)

# --- Historical yields and macro correlations ---
history_file_list = ['DGS3MO', 'DGS2', 'DGS10', 'FEDFUNDS']
yield_curves(history_file_list)
correlation(history_file_list)

plt.show()
