import numpy as np
import streamlit as st
import plotly.graph_objs as go

# Page title
st.title("Covered Call Payoff Visualizer")

st.markdown(
    "Adjust the inputs on the left and see how the **covered call P&L** changes."
)

# ========== SIDEBAR INPUTS ==========

st.sidebar.header("Inputs")

fut_price = st.sidebar.number_input("Futures entry price", value=630.0, step=1.0)
fut_lot   = st.sidebar.number_input("Futures lot size", value=15, step=1)
ce_strike = st.sidebar.number_input("Call strike price (CE)", value=650.0, step=1.0)
ce_premium = st.sidebar.number_input("Call premium (per unit)", value=10.0, step=0.5)
ce_lot    = st.sidebar.number_input("Call lot size", value=15, step=1)

# Range of possible spot prices at expiry
S_T = np.linspace(fut_price * 0.8, fut_price * 1.2, 400)

# ========== P&L CALCULATIONS ==========

# Long Futures P&L
futures_pnl = (S_T - fut_price) * fut_lot

# Short Call P&L
call_pnl = (ce_premium * ce_lot) - np.maximum(S_T - ce_strike, 0) * ce_lot

# Total covered call P&L (single line)
total_pnl = futures_pnl + call_pnl

# ========== BREAKEVEN (FORMULA APPROX + NUMERICAL CHECK) ==========

# Formula breakeven (assuming CE premium is per unit)
breakeven_formula = fut_price - (ce_premium * ce_lot) / fut_lot

# Numerical (closest point where P&L ~ 0) – safer
idx_be = np.argmin(np.abs(total_pnl))
breakeven_num = S_T[idx_be]
be_pnl = total_pnl[idx_be]

st.sidebar.markdown("### Breakeven (approx)")
st.sidebar.write(f"Formula BE ≈ {breakeven_formula:.2f}")
st.sidebar.write(f"Numeric BE ≈ {breakeven_num:.2f}")

# ========== BUILD PLOTLY FIGURE ==========

fig = go.Figure()

# P&L line
fig.add_trace(
    go.Scatter(
        x=S_T,
        y=total_pnl,
        mode="lines",
        name="Covered Call Total P&L",
        hovertemplate="Spot: %{x:.2f}<br>P&L: %{y:.2f}<extra></extra>",
    )
)

# Zero P&L line
fig.add_shape(
    type="line",
    x0=S_T.min(),
    x1=S_T.max(),
    y0=0,
    y1=0,
    line=dict(dash="dash"),
)

# Breakeven vertical line (using numeric BE)
fig.add_shape(
    type="line",
    x0=breakeven_num,
    x1=breakeven_num,
    y0=min(total_pnl),
    y1=max(total_pnl),
    line=dict(dash="dash"),
)

fig.add_annotation(
    x=breakeven_num,
    y=min(total_pnl),
    text=f"BE ≈ {breakeven_num:.2f}",
    showarrow=False,
    yshift=15,
)

fig.update_layout(
    xaxis_title="Spot Price at Expiry",
    yaxis_title="Profit / Loss",
    title="Covered Call Payoff (Single Line)",
    hovermode="x",
)

st.plotly_chart(fig, use_container_width=True)
