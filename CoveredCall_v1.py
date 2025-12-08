import numpy as np
import matplotlib.pyplot as plt
import mplcursors

# ========== USER INPUTS (CHANGE ONLY THESE) ==========

fut_lot     = 1375      # 1. Future lot size
fut_price   = 630   # 2. Future price
ce_lot      = 1250      # 3. CE lot size
ce_premium  = 8     # 4. CE Premium price
ce_strike   = 620   # CE Strike price

# ========== SPOT PRICE RANGE AT EXPIRY ==========

S_T = np.linspace(fut_price * 0.8, fut_price * 1.2, 200)

# ========== P&L CALCULATIONS ==========

# Long Futures P&L
futures_pnl = (S_T - fut_price) * fut_lot

# Short Call (CE) P&L
call_pnl = (ce_premium * ce_lot) - np.maximum(S_T - ce_strike, 0) * ce_lot

# Total Covered Call P&L
total_pnl = futures_pnl + call_pnl

# ========== PLOTTING ==========

plt.figure()
plt.axhline(0, linestyle="--")

line1, = plt.plot(S_T, futures_pnl, label="Long Futures P&L")
line2, = plt.plot(S_T, call_pnl, label="Short CE P&L")
line3, = plt.plot(S_T, total_pnl, linewidth=2, label="Covered Call Total P&L")

plt.xlabel("Spot Price at Expiry")
plt.ylabel("Profit / Loss")
plt.title("Covered Call Payoff (Futures + Short Call)")
plt.legend()
plt.grid(True)

# ========== HOVER TOOLTIP (mplcursors) ==========

cursor = mplcursors.cursor([line1, line2, line3], hover=True)

# When you hover, show Spot & P&L
cursor.connect(
    "add",
    lambda sel: sel.annotation.set_text(
        f"{sel.artist.get_label()}\nSpot: {sel.target[0]:.2f}\nP&L: {sel.target[1]:.2f}"
    )
)

plt.show()
