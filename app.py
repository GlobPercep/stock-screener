"""StockLens — Multi-Market Stock Screener."""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from stocks import MARKET_STOCKS, get_exchange_rates

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockLens",
    page_icon="\u26a1",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.html(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <style>
    /* ═══ RESET & BASE ═══ */
    *, *::before, *::after { box-sizing: border-box; }
    html { font-size: 18px; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    .stApp {
        background: linear-gradient(160deg, #08080f 0%, #0d0d1a 40%, #0f1525 100%);
        color: #e2e8f0;
        font-family: 'Courier New', Courier, monospace !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding: 1.5rem 2.5rem 2.5rem; max-width: 1440px; }

    /* ═══ GLOBAL FONT OVERRIDE ═══ */
    p, span, label, div, li, td, th, input, textarea, select, button, a {
        font-family: 'Courier New', Courier, monospace !important;
    }

    /* ═══ MOBILE ═══ */
    @media (max-width: 768px) {
        html { font-size: 15px; }
        .block-container { padding: 1rem 1.2rem 1.5rem; }
        .brand-bar { flex-direction: column; gap: 8px !important; }
        .hero-row { flex-direction: column !important; gap: 6px !important; }
    }

    /* ═══ BRAND BAR ═══ */
    .brand-bar {
        display: flex; align-items: center; gap: 18px;
        padding: 1.2rem 0 1rem; margin-bottom: 0.8rem;
    }
    .brand-icon {
        width: 48px; height: 48px; border-radius: 14px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; color: white; flex-shrink: 0;
        box-shadow: 0 4px 20px rgba(99,102,241,0.25);
    }
    .brand-name {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 2.2rem; font-weight: 700; letter-spacing: -1px;
        background: linear-gradient(135deg, #a5b4fc, #c4b5fd, #f0abfc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .brand-tag {
        font-size: 0.9rem; color: #64748b;
        background: rgba(99,102,241,0.08); padding: 6px 14px;
        border-radius: 20px; border: 1px solid rgba(99,102,241,0.15);
    }

    /* ═══ GLASS CARD ═══ */
    .glass {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 24px;
        margin-bottom: 14px;
    }

    /* ═══ NAVIGATION ═══ */
    .nav-bar {
        display: flex; gap: 4px;
        background: rgba(255,255,255,0.04);
        border-radius: 14px; padding: 5px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 1.4rem; width: fit-content;
    }
    .nav-btn {
        padding: 12px 28px; border-radius: 10px;
        font-size: 1.05rem; font-weight: 700;
        color: #94a3b8; cursor: pointer;
        text-decoration: none; transition: all 0.2s;
        border: none; background: transparent;
        font-family: 'Courier New', Courier, monospace;
    }
    .nav-btn:hover { color: #e2e8f0; background: rgba(255,255,255,0.04); }
    .nav-btn.active {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white; box-shadow: 0 4px 20px rgba(99,102,241,0.3);
    }

    /* ═══ STREAMLIT METRIC OVERRIDE ═══ */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03) !important;
        backdrop-filter: blur(24px);
        border-radius: 16px !important; padding: 24px 26px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99,102,241,0.2) !important;
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important; font-size: 0.85rem !important;
        text-transform: uppercase; letter-spacing: 1.5px;
        font-weight: 700 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important; font-weight: 700 !important;
        font-size: 1.7rem !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    /* ═══ STOCK CARDS ═══ */
    .stock-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(24px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 26px; margin-bottom: 14px;
        transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
        border-color: rgba(99,102,241,0.25);
    }
    .stock-card .ticker {
        font-family: 'Courier New', Courier, monospace; font-size: 1.4rem;
        font-weight: 700; color: #f1f5f9;
    }
    .stock-card .name { color: #64748b; font-size: 0.95rem; margin: 6px 0 16px; }
    .stock-card .price {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.9rem; font-weight: 700; color: #f1f5f9;
    }
    .stock-card .change {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.1rem; font-weight: 700; margin-top: 8px;
    }
    .change-up { color: #4ade80; }
    .change-down { color: #f87171; }

    /* ═══ HERO (CHART PAGE) ═══ */
    .hero-row {
        display: flex; flex-wrap: wrap; align-items: baseline;
        gap: 16px; margin-bottom: 24px;
    }
    .hero-ticker {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.6rem; font-weight: 700; color: #f1f5f9;
    }
    .hero-name { color: #64748b; font-size: 1.15rem; }
    .hero-price {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.1rem; font-weight: 700; color: #f1f5f9;
    }
    .hero-change {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.25rem; font-weight: 700;
        padding: 6px 14px; border-radius: 10px;
    }
    .hero-change.change-up { background: rgba(74,222,128,0.1); }
    .hero-change.change-down { background: rgba(248,113,113,0.1); }

    /* ═══ INPUTS ═══ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 1.1rem !important;
        padding: 16px 18px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03) !important;
        color: #f1f5f9 !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #4b5563 !important; font-size: 1rem !important;
    }

    /* ═══ SELECTBOX & MULTISELECT ═══ */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        color: #f1f5f9 !important;
    }
    ul[data-baseweb="menu"] {
        background: #12121f !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
    }
    ul[data-baseweb="menu"] li {
        color: #e2e8f0 !important;
    }
    ul[data-baseweb="menu"] li:hover { background: rgba(99,102,241,0.12) !important; }

    /* Multiselect tags */
    span[data-baseweb="tag"] {
        background: rgba(99,102,241,0.15) !important;
        border: 1px solid rgba(99,102,241,0.25) !important;
        border-radius: 8px !important; color: #c7d2fe !important;
    }

    /* ═══ RADIO ═══ */
    .stRadio > div { gap: 8px; }
    .stRadio > div > label {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 12px 24px;
        font-size: 1.05rem; font-weight: 700;
        color: #94a3b8;
    }

    /* ═══ CHECKBOX ═══ */
    .stCheckbox label { color: #94a3b8 !important; }
    .stCheckbox label span { font-size: 1.1rem; }

    /* ═══ EXPANDER ═══ */
    .streamlit-expanderHeader {
        font-size: 1.05rem !important; font-weight: 700 !important;
        color: #94a3b8 !important;
        background: rgba(255,255,255,0.02) !important;
        border-radius: 14px !important;
    }
    details[data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        background: transparent !important;
    }

    /* ═══ SLIDER ═══ */
    .stSlider label { color: #94a3b8 !important; font-size: 1rem !important; }

    /* ═══ DATAFRAME ═══ */
    .stDataFrame {
        border-radius: 16px !important; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* ═══ PLOTLY ═══ */
    .stPlotlyChart { border-radius: 16px; overflow: hidden; }

    /* ═══ INFO/WARNING BOXES ═══ */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        color: #94a3b8 !important;
        font-size: 1.05rem !important;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div { color: #a5b4fc !important; }

    /* ═══ SEPARATOR ═══ */
    .sep {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
        margin: 1rem 0;
    }

    /* ═══ SECTION LABEL ═══ */
    .section-label {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem; font-weight: 700;
        color: #6366f1; text-transform: uppercase;
        letter-spacing: 3px; margin-bottom: 12px;
    }

    /* ═══ FOOTER ═══ */
    .footer {
        text-align: center; color: #4b5563; font-size: 0.85rem;
        padding: 2.5rem 0 1.2rem; border-top: 1px solid rgba(255,255,255,0.03);
        margin-top: 2.5rem;
    }
    .footer a { color: #6366f1; text-decoration: none; }
    </style>
    """
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
        return "\u2014"
    if val >= 1e12:
        return f"${val/1e12:.2f}T"
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    if val >= 1e6:
        return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stocks(tickers: tuple):
    rows = []
    errors = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            if not info:
                errors.append(f"{t}: empty info")
                continue
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price is None:
                errors.append(f"{t}: no price field")
                continue
            prev = info.get("regularMarketPreviousClose") or info.get("previousClose")
            chg = round((price - prev) / prev * 100, 2) if price and prev else None
            rows.append({
                "Ticker": t,
                "Name": info.get("shortName", t),
                "Sector": info.get("sector", "\u2014"),
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
        except Exception as e:
            errors.append(f"{t}: {e}")
            continue
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Market"] = df["Ticker"].apply(market_label)
    return df, errors


CHART_COLORS = {
    "bg": "rgba(0,0,0,0)",
    "grid": "rgba(255,255,255,0.04)",
    "line": "#818cf8",
    "fill": "rgba(129,140,248,0.08)",
    "up": "#4ade80",
    "up_line": "#22c55e",
    "down": "#f87171",
    "down_line": "#ef4444",
    "vol": "rgba(129,140,248,0.08)",
    "sma1": "#fbbf24",
    "sma2": "#f472b6",
    "font": "'Courier New', Courier, monospace",
    "text": "#94a3b8",
}


# ── Brand Header ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="brand-bar">'
    '  <div class="brand-icon">\u26a1</div>'
    '  <span class="brand-name">StockLens</span>'
    '  <span class="brand-tag">US &middot; HK &middot; SG</span>'
    "</div>",
    unsafe_allow_html=True,
)

# ── Navigation (pure HTML rendered, Streamlit radio hidden) ──────────────────
page = st.radio("_nav", ["Dashboard", "Compare", "Chart"], horizontal=True, label_visibility="collapsed")

st.markdown('<div class="sep"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown('<div class="section-label">Search</div>', unsafe_allow_html=True)
    custom = st.text_input(
        "tickers", placeholder="Type tickers: AAPL, 0700.HK, D05.SI  (blank = all presets)",
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        markets = st.multiselect(
            "m", ["US", "Hong Kong", "Singapore"],
            default=["US", "Hong Kong", "Singapore"], label_visibility="collapsed",
        )
    with c2:
        to_usd = st.checkbox("USD", value=False)

    with st.expander("Filters"):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            pe_range = st.slider("P/E Range", 0.0, 100.0, (0.0, 100.0), step=1.0)
        with fc2:
            min_yield = st.slider("Min Yield %", 0.0, 15.0, 0.0, step=0.5)
        with fc3:
            cap_filter = st.selectbox("Market Cap", ["All", "> $100B", "> $10B", "> $1B", "< $1B"])

    custom_tickers = parse_tickers(custom)
    if custom_tickers:
        all_tickers = custom_tickers
    else:
        all_tickers = []
        for m in markets:
            all_tickers.extend(MARKET_STOCKS.get(m, {}).keys())

    if not all_tickers:
        st.info("Enter tickers or select a market to begin.")
        st.stop()

    with st.spinner(f"Loading {len(all_tickers)} stocks..."):
        df, fetch_errors = fetch_stocks(tuple(all_tickers))

    if df.empty:
        if fetch_errors:
            st.error("Errors:\n" + "\n".join(fetch_errors[:5]))
        st.warning("No data found. Check your tickers.")
        st.stop()
    if fetch_errors:
        with st.expander(f"{len(fetch_errors)} ticker(s) failed"):
            st.code("\n".join(fetch_errors))

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

    # Metrics
    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Stocks", len(f))
    m2.metric("Avg P/E", f"{f['P/E'].mean():.1f}" if f["P/E"].notna().any() else "\u2014")
    m3.metric("Avg Yield", f"{f['Yield %'].mean():.2f}%" if f["Yield %"].notna().any() else "\u2014")

    top = f.loc[f["Change %"].idxmax()] if f["Change %"].notna().any() else None
    bot = f.loc[f["Change %"].idxmin()] if f["Change %"].notna().any() else None
    g1, g2 = st.columns(2)
    g1.metric("Top Gainer", f"{top['Ticker']}  +{top['Change %']:.1f}%" if top is not None else "\u2014")
    g2.metric("Top Loser", f"{bot['Ticker']}  {bot['Change %']:.1f}%" if bot is not None else "\u2014")

    st.markdown("")
    st.markdown('<div class="section-label">All Stocks</div>', unsafe_allow_html=True)

    cols = ["Ticker", "Name", "Market", "Price", "Change %", "P/E", "Fwd P/E", "P/B", "Yield %", "52w High", "52w Low"]
    if to_usd:
        cols.insert(4, "USD Price")
    f = f.sort_values("Market Cap", ascending=False, na_position="last")

    st.dataframe(
        f[cols], use_container_width=True, hide_index=True,
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

    st.markdown(
        '<div class="footer">StockLens &mdash; Data from Yahoo Finance &middot; Not financial advice</div>',
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  COMPARE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Compare":

    st.markdown('<div class="section-label">Compare Stocks</div>', unsafe_allow_html=True)
    tickers_input = st.text_input(
        "ct", placeholder="Enter 2-5 tickers: AAPL, 0700.HK, D05.SI",
        label_visibility="collapsed",
    )
    pick = parse_tickers(tickers_input)

    if len(pick) < 2:
        st.info("Type at least 2 tickers separated by commas.")
        st.stop()

    with st.spinner("Loading..."):
        cdf, _ = fetch_stocks(tuple(pick))

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
    st.markdown('<div class="section-label">Details</div>', unsafe_allow_html=True)

    table_rows = []
    for _, row in cdf.iterrows():
        rate = rates.get(row["Currency"], 1.0)
        table_rows.append({
            "Ticker": row["Ticker"],
            "Name": row["Name"],
            "Mkt": row["Market"],
            "USD Price": f"${row['Price'] * rate:.2f}" if row["Price"] else "\u2014",
            "P/E": f"{row['P/E']:.1f}" if pd.notna(row["P/E"]) else "\u2014",
            "Fwd P/E": f"{row['Fwd P/E']:.1f}" if pd.notna(row["Fwd P/E"]) else "\u2014",
            "P/B": f"{row['P/B']:.2f}" if pd.notna(row["P/B"]) else "\u2014",
            "Yield": f"{row['Yield %']:.2f}%" if pd.notna(row["Yield %"]) else "\u2014",
            "Mkt Cap": fmt_cap(row["Market Cap"] * rate if row["Market Cap"] else None),
            "Beta": f"{row['Beta']:.2f}" if pd.notna(row["Beta"]) else "\u2014",
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown("")
    st.markdown('<div class="section-label">Visual</div>', unsafe_allow_html=True)
    metric = st.selectbox("Compare by", ["P/E", "Fwd P/E", "P/B", "Yield %", "Beta"])
    chart_data = cdf[["Ticker", metric]].dropna(subset=[metric])
    if not chart_data.empty:
        colors = ["#818cf8", "#f472b6", "#fbbf24", "#34d399", "#a78bfa"]
        fig = go.Figure(go.Bar(
            x=chart_data["Ticker"], y=chart_data[metric],
            text=chart_data[metric].round(2), textposition="outside",
            textfont=dict(size=14, color="#94a3b8"),
            marker_color=colors[:len(chart_data)],
            marker_cornerradius=8,
        ))
        fig.update_layout(
            height=360, yaxis_title=metric,
            plot_bgcolor=CHART_COLORS["bg"], paper_bgcolor=CHART_COLORS["bg"],
            font=dict(family=CHART_COLORS["font"], size=13, color=CHART_COLORS["text"]),
            yaxis=dict(gridcolor=CHART_COLORS["grid"]),
            xaxis=dict(gridcolor=CHART_COLORS["grid"]),
            margin=dict(t=30, b=50, l=50, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="footer">StockLens &mdash; Data from Yahoo Finance &middot; Not financial advice</div>',
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  CHART
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Chart":

    st.markdown('<div class="section-label">Price Chart</div>', unsafe_allow_html=True)
    ticker_input = st.text_input(
        "cht", placeholder="Enter a ticker: AAPL, 0700.HK, D05.SI",
        label_visibility="collapsed",
    )

    ticker = ticker_input.strip().upper() if ticker_input.strip() else None
    if not ticker:
        st.info("Enter a ticker to view its chart.")
        st.stop()

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, label_visibility="collapsed")
    with c2:
        style = st.radio("s", ["Line", "Candle"], horizontal=True, label_visibility="collapsed")
    with c3:
        sma = st.checkbox("SMA")

    with st.spinner("Loading..."):
        hist = yf.Ticker(ticker).history(period=period)

    if hist.empty:
        st.warning(f"No data for **{ticker}**.")
        st.stop()

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

    fig = go.Figure()

    if style == "Candle":
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"], name="Price",
            increasing_fillcolor=CHART_COLORS["up"], increasing_line_color=CHART_COLORS["up_line"],
            decreasing_fillcolor=CHART_COLORS["down"], decreasing_line_color=CHART_COLORS["down_line"],
        ))
    else:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"], mode="lines", name="Close",
            line=dict(color=CHART_COLORS["line"], width=2.5),
            fill="tozeroy", fillcolor=CHART_COLORS["fill"],
        ))

    if sma and len(hist) >= 20:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"].rolling(20).mean(),
            mode="lines", name="SMA 20",
            line=dict(color=CHART_COLORS["sma1"], width=1.5, dash="dot"),
        ))
        if len(hist) >= 50:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].rolling(50).mean(),
                mode="lines", name="SMA 50",
                line=dict(color=CHART_COLORS["sma2"], width=1.5, dash="dot"),
            ))

    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"], name="Volume",
        marker_color=CHART_COLORS["vol"], yaxis="y2",
    ))

    fig.update_layout(
        yaxis=dict(title="Price", gridcolor=CHART_COLORS["grid"], title_font_size=13, color=CHART_COLORS["text"]),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title="", color=CHART_COLORS["text"]),
        xaxis=dict(gridcolor=CHART_COLORS["grid"], color=CHART_COLORS["text"]),
        height=500, xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12, color=CHART_COLORS["text"])),
        plot_bgcolor=CHART_COLORS["bg"], paper_bgcolor=CHART_COLORS["bg"],
        font=dict(family=CHART_COLORS["font"], size=12, color=CHART_COLORS["text"]),
        margin=dict(t=10, b=40, l=60, r=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    _dash = "\u2014"
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("52w High", f"{info.get('fiftyTwoWeekHigh', _dash)}")
    s2.metric("52w Low", f"{info.get('fiftyTwoWeekLow', _dash)}")
    s3.metric("P/E", f"{info.get('trailingPE', _dash)}")
    s4.metric("Avg Vol", f"{info.get('averageVolume', 0):,.0f}")

    st.markdown(
        '<div class="footer">StockLens &mdash; Data from Yahoo Finance &middot; Not financial advice</div>',
        unsafe_allow_html=True,
    )
