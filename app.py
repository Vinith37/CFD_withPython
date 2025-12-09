import numpy as np
import streamlit as st
import plotly.graph_objects as go

# ================== PAYOFF ENGINE ==================

def payoff_leg(leg, S_T):
    qty = float(leg.get("qty", 1.0))
    leg_type = leg["type"].lower()
    pos = leg["pos"].lower()

    if leg_type == "future":
        entry = leg["entry"]
        return (S_T - entry) * qty if pos == "long" else (entry - S_T) * qty

    elif leg_type == "call":
        K = leg["strike"]
        premium = leg["premium"]
        intrinsic = np.maximum(S_T - K, 0)
        return (intrinsic - premium) * qty if pos == "long" else (premium - intrinsic) * qty

    elif leg_type == "put":
        K = leg["strike"]
        premium = leg["premium"]
        intrinsic = np.maximum(K - S_T, 0)
        return (intrinsic - premium) * qty if pos == "long" else (premium - intrinsic) * qty

    return np.zeros_like(S_T)


def find_breakevens(S_T, total_pnl):
    sign_changes = np.where(np.sign(total_pnl[:-1]) * np.sign(total_pnl[1:]) < 0)[0]
    breakevens = []
    for idx in sign_changes:
        x1, x2 = S_T[idx], S_T[idx + 1]
        y1, y2 = total_pnl[idx], total_pnl[idx + 1]
        be = x1 - y1 * (x2 - x1) / (y2 - y1)
        breakevens.append(be)
    return breakevens


# ================== STREAMLIT UI ==================

st.title("Futures & Options Strategy Payoff Builder")

st.sidebar.header("Global Inputs")

underlying_price = st.sidebar.number_input("Underlying Price", value=650.0, step=1.0)
price_range_pct = st.sidebar.slider("Price Range (%)", 10, 100, 30, 5)

strategy_type = st.sidebar.selectbox(
    "Strategy Type",
    ["Covered Call", "Straddle", "Strangle", "Bull Call Spread", "Bear Put Spread"],
)

direction = st.sidebar.selectbox("Strategy Position", ["Long (usual)", "Short (inverse)"])
is_short_strategy = direction.startswith("Short")

strategy_legs = []

# ================== STRATEGY DEFINITIONS ==================

if strategy_type == "Covered Call":
    fut_entry = st.sidebar.number_input("Futures Entry", value=underlying_price)
    fut_qty = st.sidebar.number_input("Futures Quantity", value=75.0)
    call_strike = st.sidebar.number_input("Call Strike", value=underlying_price + 30)
    call_premium = st.sidebar.number_input("Call Premium", value=10.0)
    call_qty = st.sidebar.number_input("Call Quantity", value=75.0)

    strategy_legs = [
        {"type": "future", "pos": "long", "entry": fut_entry, "qty": fut_qty},
        {"type": "call", "pos": "short", "strike": call_strike, "premium": call_premium, "qty": call_qty},
    ]

elif strategy_type == "Straddle":
    K = st.sidebar.number_input("Strike", value=underlying_price)
    call_premium = st.sidebar.number_input("Call Premium", value=20.0)
    put_premium = st.sidebar.number_input("Put Premium", value=18.0)
    qty = st.sidebar.number_input("Quantity per leg", value=75.0)

    strategy_legs = [
        {"type": "call", "pos": "long", "strike": K, "premium": call_premium, "qty": qty},
        {"type": "put", "pos": "long", "strike": K, "premium": put_premium, "qty": qty},
    ]

elif strategy_type == "Strangle":
    call_strike = st.sidebar.number_input("Call Strike", value=underlying_price + 30)
    call_premium = st.sidebar.number_input("Call Premium", value=12.0)
    put_strike = st.sidebar.number_input("Put Strike", value=underlying_price - 30)
    put_premium = st.sidebar.number_input("Put Premium", value=10.0)
    qty = st.sidebar.number_input("Quantity per leg", value=75.0)

    strategy_legs = [
        {"type": "call", "pos": "long", "strike": call_strike, "premium": call_premium, "qty": qty},
        {"type": "put", "pos": "long", "strike": put_strike, "premium": put_premium, "qty": qty},
    ]

elif strategy_type == "Bull Call Spread":
    lower_strike = st.sidebar.number_input("Lower Strike", value=underlying_price - 10)
    lower_premium = st.sidebar.number_input("Lower Strike Premium", value=18.0)
    higher_strike = st.sidebar.number_input("Higher Strike", value=underlying_price + 20)
    higher_premium = st.sidebar.number_input("Higher Strike Premium", value=8.0)
    qty = st.sidebar.number_input("Quantity per leg", value=75.0)

    strategy_legs = [
        {"type": "call", "pos": "long", "strike": lower_strike, "premium": lower_premium, "qty": qty},
        {"type": "call", "pos": "short", "strike": higher_strike, "premium": higher_premium, "qty": qty},
    ]

elif strategy_type == "Bear Put Spread":
    higher_strike = st.sidebar.number_input("Higher Strike", value=underlying_price + 20)
    higher_premium = st.sidebar.number_input("Higher Strike Premium", value=20.0)
    lower_strike = st.sidebar.number_input("Lower Strike", value=underlying_price - 10)
    lower_premium = st.sidebar.number_input("Lower Strike Premium", value=10.0)
    qty = st.sidebar.number_input("Quantity per leg", value=75.0)

    strategy_legs = [
        {"type": "put", "pos": "long", "strike": higher_strike, "premium": higher_premium, "qty": qty},
        {"type": "put", "pos": "short", "strike": lower_strike, "premium": lower_premium, "qty": qty},
    ]


# ================== APPLY LONG / SHORT TOGGLE ==================

if is_short_strategy:
    for leg in strategy_legs:
        leg["pos"] = "short" if leg["pos"] == "long" else "long"

# ================== PAYOFF CALCULATION ==================

low = underlying_price * (1 - price_range_pct / 100)
high = underlying_price * (1 + price_range_pct / 100)
S_T = np.linspace(low, high, 500)

total_pnl = np.zeros_like(S_T)
for leg in strategy_legs:
    total_pnl += payoff_leg(leg, S_T)

breakevens = find_breakevens(S_T, total_pnl)

# ================== PLOTTING ==================

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=S_T,
        y=total_pnl,
        mode="lines",
        name="Strategy P&L",
        hovertemplate="Spot: %{x:.2f}<br>P&L: %{y:.2f}<extra></extra>",
    )
)

# Zero line
fig.add_shape(type="line", x0=low, x1=high, y0=0, y1=0, line=dict(dash="dash"))

# Breakeven lines
for be in breakevens:
    fig.add_shape(
        type="line", x0=be, x1=be, y0=min(total_pnl), y1=max(total_pnl),
        line=dict(dash="dash", color="orange")
    )
    fig.add_annotation(x=be, y=min(total_pnl), text=f"BE {be:.1f}", showarrow=False, yshift=12)

# ✅ ✅ ✅ SPOT PRICE VERTICAL LINE — NOW IN GREEN ✅ ✅ ✅
fig.add_shape(
    type="line",
    x0=underlying_price,
    x1=underlying_price,
    y0=min(total_pnl),
    y1=max(total_pnl),
    line=dict(dash="dot", width=2, color="green"),
)

fig.add_annotation(
    x=underlying_price,
    y=max(total_pnl),
    text=f"Spot = {underlying_price:.1f}",
    showarrow=False,
    yshift=10,
)

fig.update_layout(
    title=f"{direction.split()[0]} {strategy_type} Payoff",
    xaxis_title="Spot Price at Expiry",
    yaxis_title="Profit / Loss",
    hovermode="x",
)

st.plotly_chart(fig, width="stretch")

# ================== SUMMARY ==================

st.subheader("Strategy Summary")
st.json(strategy_legs)
