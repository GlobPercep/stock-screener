"""Curated stock lists for US, HK, and SG markets, plus currency helpers."""

import yfinance as yf

# ---------------------------------------------------------------------------
# Stock universes – dict[ticker, company_name]
# ---------------------------------------------------------------------------

US_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta Platforms",
    "BRK-B": "Berkshire Hathaway",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PG": "Procter & Gamble",
    "XOM": "Exxon Mobil",
    "HD": "Home Depot",
    "MA": "Mastercard",
    "ABBV": "AbbVie",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "COST": "Costco",
    "MRK": "Merck",
    "AVGO": "Broadcom",
    "LLY": "Eli Lilly",
    "TSLA": "Tesla",
    "WMT": "Walmart",
    "CRM": "Salesforce",
    "BAC": "Bank of America",
    "NFLX": "Netflix",
    "AMD": "AMD",
    "ORCL": "Oracle",
    "DIS": "Walt Disney",
    "INTC": "Intel",
    "CSCO": "Cisco",
    "T": "AT&T",
    "PFE": "Pfizer",
    "NKE": "Nike",
}

HK_STOCKS = {
    "0700.HK": "Tencent",
    "9988.HK": "Alibaba",
    "0005.HK": "HSBC Holdings",
    "1299.HK": "AIA Group",
    "0388.HK": "HKEX",
    "2318.HK": "Ping An Insurance",
    "0941.HK": "China Mobile",
    "1810.HK": "Xiaomi",
    "9618.HK": "JD.com",
    "9888.HK": "Baidu",
    "3690.HK": "Meituan",
    "0001.HK": "CK Hutchison",
    "0016.HK": "SHK Properties",
    "2388.HK": "BOC Hong Kong",
    "0003.HK": "HK & China Gas",
    "0011.HK": "Hang Seng Bank",
    "0027.HK": "Galaxy Entertainment",
    "1928.HK": "Sands China",
    "0883.HK": "CNOOC",
    "0939.HK": "CCB",
    "1398.HK": "ICBC",
    "3988.HK": "Bank of China",
    "2628.HK": "China Life",
    "0267.HK": "CITIC",
    "1211.HK": "BYD",
}

SG_STOCKS = {
    "D05.SI": "DBS Group",
    "O39.SI": "OCBC Bank",
    "U11.SI": "UOB",
    "Z74.SI": "Singtel",
    "C38U.SI": "CapitaLand Integrated",
    "A17U.SI": "Ascendas REIT",
    "S68.SI": "SGX",
    "C09.SI": "City Developments",
    "BS6.SI": "Yangzijiang Shipbuilding",
    "BN4.SI": "Keppel",
    "Y92.SI": "Thai Beverage",
    "G13.SI": "Genting Singapore",
    "U96.SI": "Sembcorp Industries",
    "S58.SI": "SATS",
    "N2IU.SI": "Mapletree Pan Asia",
    "ME8U.SI": "Mapletree Industrial",
    "H78.SI": "Hongkong Land",
    "C6L.SI": "Singapore Airlines",
    "F34.SI": "Wilmar International",
    "V03.SI": "Venture Corporation",
}

MARKET_STOCKS = {
    "US": US_STOCKS,
    "Hong Kong": HK_STOCKS,
    "Singapore": SG_STOCKS,
}

MARKET_CURRENCY = {
    "US": "USD",
    "Hong Kong": "HKD",
    "Singapore": "SGD",
}

# Approximate fallback rates (to USD) if live fetch fails
_FALLBACK_RATES = {"USD": 1.0, "HKD": 0.128, "SGD": 0.75}


def get_exchange_rates() -> dict[str, float]:
    """Fetch live FX rates (to USD) using yfinance currency pairs."""
    rates = {"USD": 1.0}
    pairs = {"HKD": "HKDUSD=X", "SGD": "SGDUSD=X"}
    for currency, symbol in pairs.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                rates[currency] = float(hist["Close"].iloc[-1])
            else:
                rates[currency] = _FALLBACK_RATES[currency]
        except Exception:
            rates[currency] = _FALLBACK_RATES[currency]
    return rates
