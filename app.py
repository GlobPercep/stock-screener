"""Multi-Market Stock Screener — US, Hong Kong & Singapore."""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from stocks import MARKET_STOCKS, get_exchange_rates

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="StockLens", page_icon="\u26a1", layout="wide", initial_sidebar_state="collapsed")

# ── Custom CSS — monospace, large font, mobile-friendly ──────────────────────
st.markdown(
    """
    <style>
    /* ── Global: monospace font, large base size ── */
    * { font-family: 'SF Mono', 'Menlo', 'Monaco', 'Cascadia Code', 'Consolas', monospace !important; }
    html { font-size: 17px; }

    .stApp { background: #f8f9fc; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding: 1.5rem 1.5rem 1rem; max-width: 100%; }

    /* ── Viewport meta for mobile ── */
    @media (max-width: 768px) {
        html { font-size: 15px; }
        .block-container { padding: 1rem 0.75rem; }
        .stock-card { min-width: 100% !important; }
        .hero-ticker { font-size: 1.6rem !important; }
        .hero-price { font-size: 1.4rem !important; }
    }

    /* ── Logo ── */
    .logo-bar {
        display: flex; align-items: baseline; gap: 12px;
        margin-bottom: 1rem; padding-bottom: 0.75rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .logo-text {
        font-size: 2rem; font-weight: 800; letter-spacing: -1px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .logo-tag { color: #9ca3af; font-size: 0.9rem; }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: #fff; border-radius: 12px; padding: 20px;
        border: 1px solid #e5e7eb;
    }
    div[data-testid="stMetric"] label {
        color: #6b7280; font-size: 0.8rem; text-transform: uppercase;
        letter-spacing: 1px; font-weight: 700;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #111827; font-weight: 700; font-size: 1.5rem;
    }

    /* ── Stock cards (compare page) ── */
    .stock-card {
        background: #fff; border-radius: 12px; padding: 20px;
        border: 1px solid #e5e7eb; margin-bottom: 12px;
    }
    .stock-card .ticker { font-size: 1.3rem; font-weight: 800; color: #111827; }
    .stock-card .name { color: #9ca3af; font-size: 0.85rem; margin: 4px 0 12px; }
    .stock-card .price { font-size: 1.7rem; font-weight: 800; color: #111827; }
    .stock-card .change { font-size: 1rem; font-weight: 700; margin-top: 4px; }
    .change-up { color: #16a34a; }
    .change-down { color: #dc2626; }

    /* ── Hero ticker (chart page) ── */
    .hero-row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 12px; margin-bottom: 20px; }
    .hero-ticker { font-size: 2rem; font-weight: 800; color: #111827; }
    .hero-name { color: #9ca3af; font-size: 1rem; }
    .hero-price { font-size: 1.8rem; font-weight: 800; color: #111827; }
    .hero-change { font-size: 1.1rem; font-weight: 700; }

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea {
        font-size: 1rem !important; padding: 12px 14px !important;
        border-radius: 10px !important; border: 2px solid #e5e7eb !important;
        background: #fff !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }
    .stTextInput input::placeholder { color: #9ca3af !important; font-size: 0.95rem !important; }

    /* ── Selectbox & Multiselect — fix text/arrow overlap ── */
    /* The select container */
    div[data-baseweb="select"] {
        font-size: 1rem !important;
        min-height: 48px !important;
    }
    /* The value area — add big right padding so text never reaches the arrow */
    div[data-baseweb="select"] > div:first-child {
        padding: 10px 50px 10px 14px !important;
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        background: #fff !important;
        min-height: 48px !important;
        position: relative !important;
    }
    /* The arrow/icon container — pin it to the right */
    div[data-baseweb="select"] > div:first-child > div:last-child {
        position: absolute !important;
        right: 10px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        pointer-events: none;
    }
    /* The text inside — prevent it from overflowing into the arrow */
    div[data-baseweb="select"] > div:first-child > div:first-child {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        padding-right: 10px !important;
    }
    /* Multiselect selected tags area */
    div[data-baseweb="select"] > div:first-child > div:nth-child(1) {
        max-width: calc(100% - 50px) !important;
    }
    /* Dropdown menu items — also give them room */
    ul[data-baseweb="menu"] li {
        font-size: 0.95rem !important;
        padding: 10px 14px !important;
    }

    /* ── Radio pills ── */
    .stRadio > div { gap: 6px; }
    .stRadio > div > label {
        background: #f3f4f6; border-radius: 8px; padding: 10px 20px;
        font-size: 0.95rem; font-weight: 600;
    }
    .stRadio > div > label[data-checked="true"] {
        background: #6366f1; color: white;
    }

    /* ── Checkbox ── */
    .stCheckbox label span { font-size: 1rem; }

    /* ── Expander ── */
    .streamlit-expanderHeader { font-size: 1rem; font-weight: 700; }

    /* ── Dataframe — larger text ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    .stDataFrame table { font-size: 0.95rem !important; }
    .stDataFrame th { font-size: 0.85rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.5px; }

    /* ── Buttons ── */
    .stButton > button {
        background: #6366f1; color: white; border: none; border-radius: 10px;
        font-weight: 700; padding: 12px 28px; font-size: 1rem;
    }
    .stButton > button:hover { background: #4f46e5; }

    /* ── Separator ── */
    .sep { height: 2px; background: #e5e7eb; margin: 1rem 0; }

    /* ── Plotly ── */
    .stPlotlyChart { border-radius: 12px; overflow: hidden; }

    /* ── Spinner ── */
    .stSpinner > div > div { border-top-color: #6366f1 !important; }

    /* ── Multiselect tags ── */
    .stMultiSelect span[data-baseweb="tag"] {
        font-size: 0.85rem !important; padding: 4px 10px;
        max-width: 150px; overflow: hidden; text-overflow: ellipsis;
    }
    .stMultiSelect > div > div > div > div { flex-wrap: wrap; gap: 4px; }
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """,
    unsafe_allow_html=True,
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def parse_tickers(text: str) -> list[str]:
    if not text.strip():
        return []
    raw = text.replace(",", "\n").replace(";", "\n").split("\n")
    return [t.strip().upper() for t in raw if t.strip()]


def market_label(ticker: str) -> str:
    if ticker.endswith(".HK"):
        return "HK"
    if ticker.endswith(".SI"):
        return "SG"
    return "US"


def fmt_cap(val):
    if val is None:
        return "—"
    if val >= 1e12:
        return f"${val/1e12:.2f}T"
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    if val >= 1e6:
        return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stocks(tickers: tuple) -> pd.DataFrame:
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
                "Sector": info.get("sector", "—"),
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
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Market"] = df["Ticker"].apply(market_label)
    return df


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="logo-bar">'
    '  <span class="logo-text">StockLens</span>'
    '  <span class="logo-tag">US / HK / SG</span>'
    "</div>",
    unsafe_allow_html=True,
)

# ── Navigation ───────────────────────────────────────────────────────────────
page = st.radio(
    "nav", ["Dashboard", "Compare", "Chart"], horizontal=True, label_visibility="collapsed"
)

st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    # Ticker input — full width for easy mobile use
    custom = st.text_input(
        "tickers",
        placeholder="Enter tickers: AAPL, 0700.HK, D05.SI  (leave blank for all presets)",
        label_visibility="collapsed",
    )

    # Market + USD toggle in a row
    c1, c2 = st.columns([3, 1])
    with c1:
        markets = st.multiselect(
            "Markets", ["US", "Hong Kong", "Singapore"],
            default=["US", "Hong Kong", "Singapore"],
            label_visibility="collapsed",
        )
    with c2:
        to_usd = st.checkbox("USD", value=False)

    # Filters — collapsed by default to keep it clean
    with st.expander("Filters"):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            pe_range = st.slider("P/E Range", 0.0, 100.0, (0.0, 100.0), step=1.0)
        with fc2:
            min_yield = st.slider("Min Yield %", 0.0, 15.0, 0.0, step=0.5)
        with fc3:
            cap_filter = st.selectbox("Market Cap", ["All", "> $100B", "> $10B", "> $1B", "< $1B"])

    # Build ticker list
    custom_tickers = parse_tickers(custom)
    if custom_tickers:
        all_tickers = custom_tickers
    else:
        all_tickers = []
        for m in markets:
            all_tickers.extend(MARKET_STOCKS.get(m, {}).keys())

    if not all_tickers:
        st.info("Enter tickers above or select a market.")
        st.stop()

    with st.spinner(f"Loading {len(all_tickers)} stocks..."):
        df = fetch_stocks(tuple(all_tickers))

    if df.empty:
        st.warning("No data found. Check your tickers.")
        st.stop()

    # Apply filters
    f = df.copy()
    if pe_range != (0.0, 100.0):
        f = f[f["P/E"].notna() & f["P/E"].between(pe_range[0], pe_range[1])]
    if min_yield > 0:
        f = f[f["Yield %"].notna() & (f["Yield %"] >= min_yield)]
    if cap_filter == "> $100B":
        f = f[f["Market Cap"].notna() & (f["Market Cap"] >= 1e11)]
    elif cap_filter == "> $10B":
        f = f[f["Market Cap"].notna() & (f["Market Cap"] >= 1e10)]
    elif cap_filter == "> $1B":
        f = f[f["Market Cap"].notna() & (f["Market Cap"] >= 1e9)]
    elif cap_filter == "< $1B":
        f = f[f["Market Cap"].notna() & (f["Market Cap"] < 1e9)]

    if to_usd:
        rates = get_exchange_rates()
        f["USD Price"] = f.apply(
            lambda r: round(r["Price"] * rates.get(r["Currency"], 1.0), 2) if r["Price"] else None,
            axis=1,
        )

    # Metrics — 3 columns on mobile, stacks nicely
    m1, m2, m3 = st.columns(3)
    m1.metric("Stocks", len(f))
    m2.metric("Avg P/E", f"{f['P/E'].mean():.1f}" if f["P/E"].notna().any() else "—")
    m3.metric("Avg Yield", f"{f['Yield %'].mean():.2f}%" if f["Yield %"].notna().any() else "—")

    top = f.loc[f["Change %"].idxmax()] if f["Change %"].notna().any() else None
    bot = f.loc[f["Change %"].idxmin()] if f["Change %"].notna().any() else None
    g1, g2 = st.columns(2)
    g1.metric("Top Gainer", f"{top['Ticker']}  +{top['Change %']:.1f}%" if top is not None else "—")
    g2.metric("Top Loser", f"{bot['Ticker']}  {bot['Change %']:.1f}%" if bot is not None else "—")

    st.markdown("")

    # Table
    cols = ["Ticker", "Name", "Market", "Price", "Change %", "P/E", "Fwd P/E", "P/B", "Yield %", "52w High", "52w Low"]
    if to_usd:
        cols.insert(4, "USD Price")
    f = f.sort_values("Market Cap", ascending=False, na_position="last")

    st.dataframe(
        f[cols],
        use_container_width=True,
        hide_index=True,
        height=min(len(f) * 42 + 50, 650),
        column_config={
            "Price": st.column_config.NumberColumn(format="%.2f"),
            "USD Price": st.column_config.NumberColumn(format="$%.2f"),
            "Change %": st.column_config.NumberColumn(format="%.2f%%"),
            "P/E": st.column_config.NumberColumn(format="%.1f"),
            "Fwd P/E": st.column_config.NumberColumn(format="%.1f"),
            "P/B": st.column_config.NumberColumn(format="%.2f"),
            "Yield %": st.column_config.NumberColumn(format="%.2f%%"),
            "52w High": st.column_config.NumberColumn(format="%.2f"),
            "52w Low": st.column_config.NumberColumn(format="%.2f"),
        },
    )

# ═════════════════════════════════════════════════════════════════════════════
# COMPARE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Compare":

    st.markdown("**Enter 2-5 tickers to compare**")
    tickers_input = st.text_input(
        "compare_tickers",
        placeholder="AAPL, 0700.HK, D05.SI, MSFT",
        label_visibility="collapsed",
    )
    pick = parse_tickers(tickers_input)

    if len(pick) < 2:
        st.info("Type at least 2 tickers separated by commas.")
        st.stop()

    with st.spinner("Loading..."):
        cdf = fetch_stocks(tuple(pick))

    if cdf.empty:
        st.warning("No data found. Check your tickers.")
        st.stop()

    rates = get_exchange_rates()

    # Stock cards
    card_cols = st.columns(min(len(cdf), 5))
    for i, (_, row) in enumerate(cdf.iterrows()):
        rate = rates.get(row["Currency"], 1.0)
        chg = row["Change %"]
        arrow = "+" if chg and chg > 0 else ""
        chg_class = "change-up" if chg and chg > 0 else "change-down"
        with card_cols[i]:
            st.markdown(
                f'<div class="stock-card">'
                f'<div class="ticker">{row["Ticker"]}</div>'
                f'<div class="name">{row["Name"]}</div>'
                f'<div class="price">${row["Price"] * rate:.2f}</div>'
                f'<div class="change {chg_class}">{arrow}{chg:.2f}%</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("")

    # Comparison table
    table_rows = []
    for _, row in cdf.iterrows():
        rate = rates.get(row["Currency"], 1.0)
        table_rows.append({
            "Ticker": row["Ticker"],
            "Name": row["Name"],
            "Mkt": row["Market"],
            "Price (USD)": f"${row['Price'] * rate:.2f}" if row["Price"] else "—",
            "P/E": f"{row['P/E']:.1f}" if pd.notna(row["P/E"]) else "—",
            "Fwd P/E": f"{row['Fwd P/E']:.1f}" if pd.notna(row["Fwd P/E"]) else "—",
            "P/B": f"{row['P/B']:.2f}" if pd.notna(row["P/B"]) else "—",
            "Yield": f"{row['Yield %']:.2f}%" if pd.notna(row["Yield %"]) else "—",
            "Mkt Cap": fmt_cap(row["Market Cap"] * rate if row["Market Cap"] else None),
            "Beta": f"{row['Beta']:.2f}" if pd.notna(row["Beta"]) else "—",
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # Bar chart
    st.markdown("")
    metric = st.selectbox("Compare by", ["P/E", "Fwd P/E", "P/B", "Yield %", "Beta"])
    chart_data = cdf[["Ticker", metric]].dropna(subset=[metric])
    if not chart_data.empty:
        colors = ["#6366f1", "#ec4899", "#f59e0b", "#10b981", "#8b5cf6"]
        fig = go.Figure(go.Bar(
            x=chart_data["Ticker"], y=chart_data[metric],
            text=chart_data[metric].round(2), textposition="outside",
            textfont=dict(size=14, family="Menlo, monospace"),
            marker_color=colors[:len(chart_data)],
            marker_cornerradius=6,
        ))
        fig.update_layout(
            height=360, yaxis_title=metric,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Menlo, SF Mono, monospace", size=13),
            margin=dict(t=30, b=50),
        )
        st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# CHART
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Chart":

    # Simple input row
    ticker_input = st.text_input(
        "chart_ticker",
        placeholder="Enter a ticker: AAPL, 0700.HK, D05.SI",
        label_visibility="collapsed",
    )

    ticker = ticker_input.strip().upper() if ticker_input.strip() else None
    if not ticker:
        st.info("Enter a ticker above to view its chart.")
        st.stop()

    # Controls row
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, label_visibility="collapsed")
    with c2:
        style = st.radio("Style", ["Line", "Candle"], horizontal=True, label_visibility="collapsed")
    with c3:
        sma = st.checkbox("SMA")

    with st.spinner("Loading..."):
        hist = yf.Ticker(ticker).history(period=period)

    if hist.empty:
        st.warning(f"No data for **{ticker}**.")
        st.stop()

    # Hero stats
    info = yf.Ticker(ticker).info
    name = info.get("shortName", ticker)
    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)
    chg = ((price - prev) / prev * 100) if price and prev else 0
    chg_class = "change-up" if chg >= 0 else "change-down"

    st.markdown(
        f'<div class="hero-row">'
        f'  <span class="hero-ticker">{ticker}</span>'
        f'  <span class="hero-name">{name}</span>'
        f'  <span class="hero-price">{info.get("currency","")}&nbsp;{price:.2f}</span>'
        f'  <span class="hero-change {chg_class}">{"+" if chg >= 0 else ""}{chg:.2f}%</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Chart
    fig = go.Figure()

    if style == "Candle":
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"], name="Price",
            increasing_fillcolor="#22c55e", increasing_line_color="#16a34a",
            decreasing_fillcolor="#ef4444", decreasing_line_color="#dc2626",
        ))
    else:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"], mode="lines", name="Close",
            line=dict(color="#6366f1", width=2.5),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.06)",
        ))

    if sma and len(hist) >= 20:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"].rolling(20).mean(),
            mode="lines", name="SMA 20", line=dict(color="#f59e0b", width=1.5, dash="dot"),
        ))
        if len(hist) >= 50:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].rolling(50).mean(),
                mode="lines", name="SMA 50", line=dict(color="#ec4899", width=1.5, dash="dot"),
            ))

    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"], name="Volume",
        marker_color="rgba(99,102,241,0.1)", yaxis="y2",
    ))

    fig.update_layout(
        yaxis=dict(title="Price", gridcolor="#f1f5f9", title_font_size=14),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title=""),
        xaxis=dict(gridcolor="#f1f5f9"),
        height=500, xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=13)),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Menlo, SF Mono, monospace", size=13),
        margin=dict(t=10, b=40, l=60, r=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bottom stats
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("52w High", f"{info.get('fiftyTwoWeekHigh', '—')}")
    s2.metric("52w Low", f"{info.get('fiftyTwoWeekLow', '—')}")
    s3.metric("P/E", f"{info.get('trailingPE', '—')}")
    s4.metric("Avg Vol", f"{info.get('averageVolume', 0):,.0f}")
