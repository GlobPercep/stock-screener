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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    /* ═══ RESET & BASE ═══ */
    *, *::before, *::after { box-sizing: border-box; margin: 0; }
    html { font-size: 16px; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    .stApp {
        background: #0a0a12;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding: 1.8rem 3rem 3rem; max-width: 1500px; }

    /* ═══ GLOBAL FONT ═══ */
    p, span, label, div, li, td, th, button, a {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    input, textarea, select, code, pre {
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    }

    /* ═══ MOBILE ═══ */
    @media (max-width: 768px) {
        html { font-size: 14px; }
        .block-container { padding: 1rem 1.2rem 1.5rem; }
        .brand-bar { flex-direction: column; gap: 10px !important; }
        .hero-row { flex-direction: column !important; gap: 8px !important; }
        .stock-card { padding: 18px; }
    }

    /* ═══ BRAND BAR ═══ */
    .brand-bar {
        display: flex; align-items: center; gap: 16px;
        padding: 1.5rem 0 1.2rem; margin-bottom: 0.5rem;
    }
    .brand-icon {
        width: 44px; height: 44px; border-radius: 12px;
        background: linear-gradient(135deg, #7c3aed, #6366f1);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; color: white; flex-shrink: 0;
        box-shadow: 0 0 24px rgba(124,58,237,0.3), 0 0 48px rgba(99,102,241,0.1);
    }
    .brand-name {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 50%, #ddd6fe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .brand-tag {
        font-size: 0.7rem; color: #6366f1; font-weight: 600;
        background: rgba(99,102,241,0.08); padding: 5px 12px;
        border-radius: 6px; border: 1px solid rgba(99,102,241,0.12);
        letter-spacing: 1px; text-transform: uppercase;
    }

    /* ═══ CARDS ═══ */
    .glass {
        background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px; padding: 28px;
        margin-bottom: 16px;
    }

    /* ═══ STREAMLIT METRIC OVERRIDE ═══ */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%) !important;
        border-radius: 20px !important;
        padding: 28px 28px 24px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
        opacity: 0;
        transition: opacity 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99,102,241,0.15) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3), 0 0 40px rgba(99,102,241,0.05);
    }
    div[data-testid="stMetric"]:hover::before { opacity: 1; }
    div[data-testid="stMetric"] label {
        color: #64748b !important; font-size: 0.7rem !important;
        text-transform: uppercase; letter-spacing: 1.8px;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important; font-weight: 700 !important;
        font-size: 1.65rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.5px;
    }

    /* ═══ STOCK CARDS ═══ */
    .stock-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px; padding: 28px; margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
    }
    .stock-card::after {
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px; opacity: 0;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        transition: opacity 0.3s;
    }
    .stock-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 60px rgba(99,102,241,0.06);
        border-color: rgba(99,102,241,0.2);
    }
    .stock-card:hover::after { opacity: 1; }
    .stock-card .ticker {
        font-family: 'JetBrains Mono', monospace; font-size: 1.1rem;
        font-weight: 700; color: #e2e8f0; letter-spacing: 0.5px;
    }
    .stock-card .name {
        color: #475569; font-size: 0.78rem; margin: 4px 0 18px;
        font-weight: 500;
    }
    .stock-card .price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.65rem; font-weight: 700; color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .stock-card .change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem; font-weight: 600; margin-top: 8px;
        display: inline-block; padding: 3px 10px;
        border-radius: 6px;
    }
    .change-up { color: #4ade80; background: rgba(74,222,128,0.08); }
    .change-down { color: #f87171; background: rgba(248,113,113,0.08); }

    /* ═══ HERO (CHART PAGE) ═══ */
    .hero-row {
        display: flex; flex-wrap: wrap; align-items: baseline;
        gap: 16px; margin-bottom: 28px;
        padding: 24px 0;
    }
    .hero-ticker {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.4rem; font-weight: 800; color: #f8fafc;
        letter-spacing: -1px;
    }
    .hero-name { color: #475569; font-size: 1rem; font-weight: 500; }
    .hero-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem; font-weight: 700; color: #f1f5f9;
        letter-spacing: -0.5px;
    }
    .hero-change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem; font-weight: 700;
        padding: 6px 16px; border-radius: 10px;
    }
    .hero-change.change-up { background: rgba(74,222,128,0.1); color: #4ade80; }
    .hero-change.change-down { background: rgba(248,113,113,0.1); color: #f87171; }

    /* ═══ INPUTS ═══ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
        padding: 14px 18px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03) !important;
        color: #f1f5f9 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1), 0 0 20px rgba(99,102,241,0.05) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #374151 !important; font-size: 0.88rem !important;
    }

    /* ═══ SELECTBOX & MULTISELECT ═══ */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        color: #f1f5f9 !important;
    }
    ul[data-baseweb="menu"] {
        background: #111119 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5) !important;
    }
    ul[data-baseweb="menu"] li { color: #e2e8f0 !important; }
    ul[data-baseweb="menu"] li:hover { background: rgba(99,102,241,0.1) !important; }

    span[data-baseweb="tag"] {
        background: rgba(99,102,241,0.12) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 8px !important; color: #a5b4fc !important;
        font-weight: 500 !important;
    }

    /* ═══ RADIO ═══ */
    .stRadio > div { gap: 6px; }
    .stRadio > div > label {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px; padding: 10px 22px;
        font-size: 0.9rem; font-weight: 600;
        color: #94a3b8;
        transition: all 0.2s;
    }

    /* ═══ CHECKBOX ═══ */
    .stCheckbox label { color: #94a3b8 !important; }
    .stCheckbox label span { font-size: 0.95rem; }

    /* ═══ EXPANDER ═══ */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important; font-weight: 600 !important;
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
    .stSlider label { color: #64748b !important; font-size: 0.85rem !important; font-weight: 500 !important; }

    /* ═══ DATAFRAME ═══ */
    .stDataFrame {
        border-radius: 18px !important; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* ═══ PLOTLY ═══ */
    .stPlotlyChart { border-radius: 18px; overflow: hidden; }

    /* ═══ INFO/WARNING BOXES ═══ */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        color: #94a3b8 !important;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div { color: #818cf8 !important; }

    /* ═══ SEPARATOR ═══ */
    .sep {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        margin: 0.6rem 0 1.2rem;
    }

    /* ═══ SECTION LABEL ═══ */
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

    /* ═══ FOOTER ═══ */
    .footer {
        text-align: center; color: #334155; font-size: 0.75rem;
        padding: 3rem 0 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.03);
        margin-top: 3rem; font-weight: 500;
        letter-spacing: 0.5px;
    }
    .footer a { color: #6366f1; text-decoration: none; }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.08);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }
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
    "grid": "rgba(255,255,255,0.03)",
    "line": "#818cf8",
    "fill": "rgba(129,140,248,0.06)",
    "up": "#4ade80",
    "up_line": "#22c55e",
    "down": "#f87171",
    "down_line": "#ef4444",
    "vol": "rgba(129,140,248,0.06)",
    "sma1": "#fbbf24",
    "sma2": "#f472b6",
    "font": "Inter, -apple-system, sans-serif",
    "text": "#64748b",
}


# ── Brand Header ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="brand-bar">'
    '  <div class="brand-icon">S</div>'
    '  <span class="brand-name">StockLens</span>'
    '  <span class="brand-tag">Multi-Market Screener</span>'
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
