import numpy as np
import matplotlib.pyplot as plt
import mplcursors

# ========== USER INPUTS (CHANGE ONLY THESE) ==========

fut_lot     = 1325      # Futures lot size
fut_price   = 630     # Futures entry price
ce_lot      = 1250      # CE lot size
ce_premium  = 8      # CE premium (per unit)
ce_strike   = 620     # CE strike price

# ========== SPOT PRICE RANGE AT EXPIRY ==========

S_T = np.linspace(fut_price * 0.8, fut_price * 1.2, 400)

# ========== P&L CALCULATIONS ==========

futures_pnl = (S_T - fut_price) * fut_lot
call_pnl    = (ce_premium * ce_lot) - np.maximum(S_T - ce_strike, 0) * ce_lot
total_pnl   = futures_pnl + call_pnl   # single consolidated line

# ========== BREAKEVEN (NUMERICAL) ==========

idx_be   = np.argmin(np.abs(total_pnl))
breakeven = S_T[idx_be]
be_pnl    = total_pnl[idx_be]
print(f"Approx breakeven spot: {breakeven:.2f}, P&L ≈ {be_pnl:.2f}")

# ========== PLOTTING ==========

fig, ax = plt.subplots(figsize=(8, 6))

ax.axhline(0, linestyle="--")              # zero P&L line
line, = ax.plot(S_T, total_pnl, linewidth=2, label="Covered Call Total P&L")

# draw breakeven vertical line
ax.axvline(breakeven, linestyle="--")

# get current y-limits and place text near the bottom
ymin, ymax = ax.get_ylim()
y_text = ymin + 0.05 * (ymax - ymin)       # 5% above bottom

ax.text(
    breakeven,
    y_text,
    f"BE ≈ {breakeven:.2f}",
    rotation=90,
    va="bottom",
    ha="left",
    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", alpha=0.7)
)

ax.set_xlabel("Spot Price at Expiry")
ax.set_ylabel("Profit / Loss")
ax.set_title("Covered Call Payoff (Single Line with Breakeven)")
ax.legend()
ax.grid(True)

# ========== HOVER TOOLTIP ==========

cursor = mplcursors.cursor(line, hover=True)
cursor.connect(
    "add",
    lambda sel: sel.annotation.set_text(
        f"Spot: {sel.target[0]:.2f}\nTotal P&L: {sel.target[1]:.2f}"
    )
)

plt.show()
