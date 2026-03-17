"""StockLens — Stock Peer Analysis Dashboard."""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from stocks import MARKET_STOCKS, get_exchange_rates

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockLens",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.html(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; }
    html { font-size: 16px; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    .stApp {
        background: #0a0a12;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1500px; }

    p, span, label, div, li, td, th, button, a {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    input, textarea, select, code, pre {
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    }

    /* Containers with border */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 20px !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: transparent !important;
        border: none !important;
        padding: 8px 4px !important;
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important; font-size: 0.7rem !important;
        text-transform: uppercase; letter-spacing: 1.8px;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important; font-weight: 700 !important;
        font-size: 1.5rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.5px;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03) !important;
        color: #f1f5f9 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    }

    /* Select / Multiselect */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
    }
    ul[data-baseweb="menu"] {
        background: #111119 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5) !important;
    }
    ul[data-baseweb="menu"] li { color: #e2e8f0 !important; }
    ul[data-baseweb="menu"] li:hover { background: rgba(99,102,241,0.1) !important; }
    span[data-baseweb="tag"] {
        background: rgba(99,102,241,0.12) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 8px !important; color: #a5b4fc !important;
    }

    /* Pills */
    div[data-testid="stPills"] button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }

    /* Expander */
    details[data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        background: transparent !important;
    }

    /* Slider */
    .stSlider label { color: #64748b !important; font-size: 0.82rem !important; font-weight: 500 !important; }

    /* DataFrame */
    .stDataFrame {
        border-radius: 16px !important; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Plotly / Altair */
    .stPlotlyChart, .stVegaLiteChart { border-radius: 16px; overflow: hidden; }

    /* Info/Warning */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        color: #94a3b8 !important;
    }

    /* Section label */
    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem; font-weight: 700;
        color: #6366f1; text-transform: uppercase;
        letter-spacing: 3px; margin-bottom: 14px;
        display: flex; align-items: center; gap: 10px;
    }
    .section-label::after {
        content: '';
        flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(99,102,241,0.2), transparent);
    }

    /* Stock cards */
    .stock-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px; padding: 24px; margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
    }
    .stock-card::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0;
        height: 3px; opacity: 0;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        transition: opacity 0.3s;
    }
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.4);
        border-color: rgba(99,102,241,0.2);
    }
    .stock-card:hover::after { opacity: 1; }
    .stock-card .ticker {
        font-family: 'JetBrains Mono', monospace; font-size: 1.05rem;
        font-weight: 700; color: #e2e8f0;
    }
    .stock-card .name { color: #475569; font-size: 0.75rem; margin: 3px 0 14px; font-weight: 500; }
    .stock-card .price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.5px;
    }
    .stock-card .change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem; font-weight: 600; margin-top: 6px;
        display: inline-block; padding: 2px 8px; border-radius: 6px;
    }
    .change-up { color: #4ade80; background: rgba(74,222,128,0.08); }
    .change-down { color: #f87171; background: rgba(248,113,113,0.08); }

    /* Hero */
    .hero-row {
        display: flex; flex-wrap: wrap; align-items: baseline;
        gap: 14px; margin-bottom: 24px; padding: 20px 0;
    }
    .hero-ticker {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem; font-weight: 800; color: #f8fafc;
    }
    .hero-name { color: #475569; font-size: 0.95rem; font-weight: 500; }
    .hero-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem; font-weight: 700; color: #f1f5f9;
    }
    .hero-change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem; font-weight: 700;
        padding: 5px 14px; border-radius: 8px;
    }
    .hero-change.change-up { background: rgba(74,222,128,0.1); color: #4ade80; }
    .hero-change.change-down { background: rgba(248,113,113,0.1); color: #f87171; }

    /* Footer */
    .footer {
        text-align: center; color: #334155; font-size: 0.72rem;
        padding: 2.5rem 0 1.2rem;
        border-top: 1px solid rgba(255,255,255,0.03);
        margin-top: 2.5rem; font-weight: 500; letter-spacing: 0.5px;
    }

    /* Radio */
    .stRadio > div > label {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px; padding: 8px 20px;
        font-size: 0.88rem; font-weight: 600; color: #94a3b8;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }

    /* Mobile */
    @media (max-width: 768px) {
        html { font-size: 14px; }
        .block-container { padding: 1rem 1rem 1.5rem; }
    }
    </style>
    """
)

# ── Header ───────────────────────────────────────────────────────────────────

"""
# :material/query_stats: StockLens

Easily compare stocks against their peers across US, HK, and SG markets.
"""

""  # spacer

# ── Stock lists ──────────────────────────────────────────────────────────────

ALL_TICKERS = sorted(
    list(MARKET_STOCKS.get("US", {}).keys())
    + list(MARKET_STOCKS.get("Hong Kong", {}).keys())
    + list(MARKET_STOCKS.get("Singapore", {}).keys())
)

DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA", "META"]

HORIZON_MAP = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}


def stocks_to_str(stocks):
    return ",".join(stocks)


# Sync with URL query params
if "tickers_input" not in st.session_state:
    st.session_state.tickers_input = st.query_params.get(
        "stocks", stocks_to_str(DEFAULT_STOCKS)
    ).split(",")


# ── Data loading ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False, ttl=21600)
def load_history(tickers_str, period):
    """Fetch historical close prices for multiple tickers."""
    try:
        tickers_obj = yf.Tickers(tickers_str)
        data = tickers_obj.history(period=period)
    except Exception:
        return None
    if data is None or data.empty:
        return None
    # Handle MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            data = data["Close"]
        else:
            return None
    elif "Close" in data.columns:
        data = data[["Close"]]
    # Flatten column index if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)
    # Drop rows where ALL values are NaN, then forward-fill gaps
    data = data.dropna(how="all")
    data = data.ffill()
    return data


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_info(tickers: tuple):
    """Fetch current info for stock cards."""
    rows = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            if not info:
                continue
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price is None:
                continue
            prev = info.get("regularMarketPreviousClose") or info.get("previousClose")
            chg = round((price - prev) / prev * 100, 2) if price and prev else None
            rows.append({
                "Ticker": t,
                "Name": info.get("shortName", t),
                "Currency": info.get("currency", ""),
                "Price": price,
                "Change %": chg,
                "Market Cap": info.get("marketCap"),
                "P/E": info.get("trailingPE"),
                "Fwd P/E": info.get("forwardPE"),
                "P/B": info.get("priceToBook"),
                "Yield %": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
                "52w High": info.get("fiftyTwoWeekHigh"),
                "52w Low": info.get("fiftyTwoWeekLow"),
                "Beta": info.get("beta"),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


# ── Layout: Left panel + Right chart ────────────────────────────────────────

cols = st.columns([1, 3])

top_left = cols[0].container(border=True)

with top_left:
    tickers = st.multiselect(
        "Stock tickers",
        options=sorted(set(ALL_TICKERS) | set(st.session_state.tickers_input)),
        default=st.session_state.tickers_input,
        placeholder="Choose stocks to compare",
    )

    horizon = st.pills(
        "Time horizon",
        options=list(HORIZON_MAP.keys()),
        default="6 Months",
    )

tickers = [t.upper() for t in tickers]

# Sync URL
if tickers:
    st.query_params["stocks"] = stocks_to_str(tickers)
else:
    st.query_params.pop("stocks", None)

if not tickers:
    top_left.info("Pick some stocks to compare", icon=":material/info:")
    st.stop()

# ── Load data ────────────────────────────────────────────────────────────────

right_cell = cols[1].container(border=True)

with st.spinner("Loading market data..."):
    tickers_str = " ".join(tickers)
    data = load_history(tickers_str, HORIZON_MAP[horizon])

if data is None or data.empty:
    st.warning("Could not load data. Try again later.")
    st.stop()

# Handle single ticker (Series) vs multiple (DataFrame)
if isinstance(data, pd.Series):
    data = data.to_frame(name=tickers[0])

# Ensure columns are strings
data.columns = [str(c) for c in data.columns]

# Match tickers to actual column names (case-insensitive)
col_map = {c.upper(): c for c in data.columns}
matched_tickers = []
for t in tickers:
    if t in data.columns:
        matched_tickers.append(t)
    elif t.upper() in col_map:
        data = data.rename(columns={col_map[t.upper()]: t})
        matched_tickers.append(t)

# Drop columns with all NaN
empty_cols = [c for c in matched_tickers if data[c].isna().all()]
if empty_cols:
    st.error(f"No data for: {', '.join(empty_cols)}")
    matched_tickers = [t for t in matched_tickers if t not in empty_cols]

# Keep only matched columns
data = data[[c for c in matched_tickers if c in data.columns]]
tickers = [t for t in matched_tickers if t in data.columns]

if data.empty or not tickers:
    st.warning("No valid data remaining.")
    st.stop()

# ── Normalize prices ─────────────────────────────────────────────────────────

# Use first non-NaN value per column for normalization
first_valid = data.apply(lambda col: col.dropna().iloc[0] if col.dropna().any() else 1.0)
normalized = data.div(first_valid)

# Build latest values safely
latest = {}
for t in tickers:
    try:
        val = normalized[t].dropna().iloc[-1]
        latest[val] = t
    except (IndexError, KeyError):
        continue

if not latest:
    st.warning("Could not normalize data.")
    st.stop()

best_val, best_ticker = max(latest.items())
worst_val, worst_ticker = min(latest.items())

# ── Left panel: metrics ──────────────────────────────────────────────────────

bottom_left = cols[0].container(border=True)

with bottom_left:
    mc1, mc2 = st.columns(2)
    mc1.metric(
        "Best stock", best_ticker,
        delta=f"{round(best_val * 100)}%",
    )
    mc2.metric(
        "Worst stock", worst_ticker,
        delta=f"{round(worst_val * 100)}%",
    )

# ── Right panel: normalized chart ────────────────────────────────────────────

PLOTLY_COLORS = [
    "#818cf8", "#f472b6", "#fbbf24", "#34d399", "#a78bfa",
    "#fb923c", "#38bdf8", "#f87171", "#4ade80", "#e879f9",
]

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#64748b"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.06)"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        font=dict(size=11, color="#94a3b8"),
    ),
    margin=dict(t=20, b=40, l=50, r=20),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1a1a2e", bordercolor="rgba(255,255,255,0.1)",
        font=dict(size=12, color="#e2e8f0", family="JetBrains Mono"),
    ),
)

with right_cell:
    fig = go.Figure()
    for i, t in enumerate(tickers):
        fig.add_trace(go.Scatter(
            x=normalized.index, y=normalized[t],
            mode="lines", name=t,
            line=dict(color=PLOTLY_COLORS[i % len(PLOTLY_COLORS)], width=2.5),
            hovertemplate="%{y:.3f}<extra>" + t + "</extra>",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=420,
        yaxis_title="Normalized price",
        xaxis=dict(
            **PLOTLY_LAYOUT["xaxis"],
            rangeslider=dict(visible=True, thickness=0.04, bgcolor="rgba(255,255,255,0.02)"),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
                bgcolor="rgba(255,255,255,0.05)",
                activecolor="rgba(99,102,241,0.3)",
                font=dict(color="#94a3b8", size=11),
            ),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})

# ── Peer analysis section ────────────────────────────────────────────────────

""
""

st.markdown('<div class="section-label">Individual stocks vs peer average</div>', unsafe_allow_html=True)

if len(tickers) <= 1:
    st.info("Pick 2 or more tickers to see peer comparisons.")
else:
    PEER_LAYOUT = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#64748b"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(size=10, color="#94a3b8")),
        margin=dict(t=35, b=10, l=40, r=10),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1a1a2e", bordercolor="rgba(255,255,255,0.1)",
            font=dict(size=11, color="#e2e8f0", family="JetBrains Mono"),
        ),
    )

    NUM_COLS = 4
    grid_cols = st.columns(NUM_COLS)

    for i, ticker in enumerate(tickers):
        peers = normalized.drop(columns=[ticker])
        peer_avg = peers.mean(axis=1)

        # Stock vs peer average
        fig_vs = go.Figure()
        fig_vs.add_trace(go.Scatter(
            x=normalized.index, y=normalized[ticker],
            mode="lines", name=ticker,
            line=dict(color="#818cf8", width=2.5),
            hovertemplate="%{y:.3f}<extra>" + ticker + "</extra>",
        ))
        fig_vs.add_trace(go.Scatter(
            x=normalized.index, y=peer_avg,
            mode="lines", name="Peer avg",
            line=dict(color="#475569", width=2, dash="dot"),
            hovertemplate="%{y:.3f}<extra>Peer avg</extra>",
        ))
        fig_vs.update_layout(
            **PEER_LAYOUT, height=280,
            title=dict(text=f"{ticker} vs peer average", font=dict(size=13, color="#e2e8f0")),
        )

        cell = grid_cols[(i * 2) % NUM_COLS].container(border=True)
        cell.write("")
        cell.plotly_chart(fig_vs, use_container_width=True, config={"displayModeBar": False})

        # Delta area chart
        delta = normalized[ticker] - peer_avg
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Scatter(
            x=normalized.index, y=delta,
            mode="lines", name="Delta",
            line=dict(color="#818cf8", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(129,140,248,0.12)",
            hovertemplate="%{y:.3f}<extra>Delta</extra>",
        ))
        fig_delta.update_layout(
            **PEER_LAYOUT, height=280, showlegend=False,
            title=dict(text=f"{ticker} minus peer avg", font=dict(size=13, color="#e2e8f0")),
        )

        cell = grid_cols[(i * 2 + 1) % NUM_COLS].container(border=True)
        cell.write("")
        cell.plotly_chart(fig_delta, use_container_width=True, config={"displayModeBar": False})

# ── Stock detail cards ───────────────────────────────────────────────────────

""
""

st.markdown('<div class="section-label">Stock Details</div>', unsafe_allow_html=True)

with st.spinner("Loading stock details..."):
    info_df = fetch_stock_info(tuple(tickers))

if not info_df.empty:
    rates = get_exchange_rates()

    card_cols = st.columns(min(len(info_df), 5))
    for i, (_, row) in enumerate(info_df.iterrows()):
        rate = rates.get(row["Currency"], 1.0)
        chg = row["Change %"]
        arrow = "+" if chg and chg > 0 else ""
        chg_class = "change-up" if chg and chg > 0 else "change-down"
        with card_cols[i % 5]:
            st.markdown(
                f'<div class="stock-card">'
                f'<div class="ticker">{row["Ticker"]}</div>'
                f'<div class="name">{row["Name"]}</div>'
                f'<div class="price">${row["Price"] * rate:.2f}</div>'
                f'<div class="change {chg_class}">{arrow}{chg:.2f}%</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    ""

    with st.expander("Detailed metrics"):
        detail_rows = []
        for _, row in info_df.iterrows():
            rate = rates.get(row["Currency"], 1.0)
            _dash = "\u2014"
            detail_rows.append({
                "Ticker": row["Ticker"],
                "Name": row["Name"],
                "USD Price": f"${row['Price'] * rate:.2f}" if row["Price"] else _dash,
                "P/E": f"{row['P/E']:.1f}" if pd.notna(row["P/E"]) else _dash,
                "Fwd P/E": f"{row['Fwd P/E']:.1f}" if pd.notna(row["Fwd P/E"]) else _dash,
                "P/B": f"{row['P/B']:.2f}" if pd.notna(row["P/B"]) else _dash,
                "Yield": f"{row['Yield %']:.2f}%" if pd.notna(row["Yield %"]) else _dash,
                "Beta": f"{row['Beta']:.2f}" if pd.notna(row["Beta"]) else _dash,
            })
        st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

# ── Raw data ─────────────────────────────────────────────────────────────────

""
""

st.markdown('<div class="section-label">Raw Price Data</div>', unsafe_allow_html=True)
st.dataframe(data, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="footer">StockLens &mdash; Data from Yahoo Finance &middot; Not financial advice</div>',
    unsafe_allow_html=True,
)
