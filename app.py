import json
import os
import uuid
from datetime import datetime, time, timedelta
from io import StringIO
from urllib.parse import quote

import pandas as pd
import pytz
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# 1. PAGE CONFIG & CONSTANTS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Real-Time Sector & Stock Breakout Scanner",
    page_icon="📈",
    layout="wide",
)

IST = pytz.timezone("Asia/Kolkata")
DAILY_RESET_TIME = time(9, 10)  # 9:10 AM IST
CUSTOM_STOCKS_FILE = "custom_stocks.json"
MAX_CUSTOM_ENTRIES = 700

SIGNAL_OPTIONS = [
    "🚀 STRONG BULL (PDH + 15m)",
    "🔻 STRONG BEAR (PDL + 15m)",
    "🟢 Crossed PDH",
    "🔴 Crossed PDL",
    "🟩 Crossed 15m High",
    "🟥 Crossed 15m Low",
    "⚪ Inside Range",
]

DEFAULT_SECTORS = {
    "NIFTY 50": "^NSEI",
    "NIFTY CEMENT": "NIFTY_CEMENT.NS",
    "NIFTY IT": "^CNXIT",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY INFRA": "^CNXINFRA",
    "NIFTY PSU BANK": "^CNXPSUBANK",
    "NIFTY MEDIA": "^CNXMEDIA",
    "NIFTY FIN SERVICE": "NIFTY_FIN_SERVICE.NS",
    "NIFTY PVT BANK": "NIFTY_PVT_BANK.NS",
    "NIFTY HEALTHCARE": "NIFTY_HEALTHCARE.NS",
    "NIFTY CONSUMER DUR": "NIFTY_CONSR_DURBL.NS",
    "NIFTY OIL & GAS": "NIFTY_OIL_AND_GAS.NS",
    "NIFTY FINSEREXBNK": "NIFTY_FINSEREXBNK.NS",
    "NIFTY RAILWAYSPSU": "NIFTY_RAILWAYSPSU.NS",
    "NIFTY MS IT TELCM": "NIFTY_MS_IT_TELCM.NS",
    "NIFTY PSE": "^CNXPSE",
    "NIFTY SERVICES": "^CNXSERVICE",
    "NIFTY CPSE": "CPSE.NS",
    "NIFTY INDIA DEFENCE": "MODEFENCE.NS",
    "NIFTY INDIA MFG": "NIFTY_INDIA_MFG.NS",
    "NIFTY CAPITAL MKT": "NIFTY_CAPITAL_MKT.NS",
    "NIFTY CHEMICALS": "NIFTY_CHEMICALS.NS",
    "NIFTY HOUSING": "NIFTY_HOUSING.NS",
    "NIFTY TRANS & LOG": "NIFTY_TRANS_LOGIS.NS",
}

TV_SYMBOL_OVERRIDES = {
    "^NSEI": "NSE:NIFTY",
    "^NSEBANK": "NSE:BANKNIFTY",
    "^CNXIT": "NSE:CNXIT",
    "^CNXAUTO": "NSE:CNXAUTO",
    "^CNXPHARMA": "NSE:CNXPHARMA",
    "^CNXFMCG": "NSE:CNXFMCG",
    "^CNXMETAL": "NSE:CNXMETAL",
    "^CNXREALTY": "NSE:CNXREALTY",
    "^CNXENERGY": "NSE:CNXENERGY",
    "^CNXINFRA": "NSE:CNXINFRA",
    "^CNXPSUBANK": "NSE:CNXPSUBANK",
    "^CNXMEDIA": "NSE:CNXMEDIA",
    "^CNXPSE": "NSE:CNXPSE",
    "^CNXSERVICE": "NSE:CNXSERVICE",
    "NIFTY_CEMENT.NS": "NSE:NIFTY_CEMENT",
    "NIFTY_FIN_SERVICE.NS": "NSE:CNXFIN",
    "NIFTY_PVT_BANK.NS": "NSE:NIFTY_PVT_BANK",
    "NIFTY_HEALTHCARE.NS": "NSE:NIFTY_HEALTHCARE",
    "NIFTY_CONSR_DURBL.NS": "NSE:NIFTY_CONSR_DURBL",
    "NIFTY_OIL_AND_GAS.NS": "NSE:NIFTY_OIL_AND_GAS",
    "NIFTY_FINSEREXBNK.NS": "NSE:NIFTY_FINSEREXBNK",
    "NIFTY_RAILWAYSPSU.NS": "NSE:NIFTY_RAILWAYSPSU",
    "NIFTY_MS_IT_TELCM.NS": "NSE:NIFTY_MS_IT_TELCM",
    "CPSE.NS": "NSE:CPSE",
    "MODEFENCE.NS": "NSE:NIFTYINDIA_DEFENCE",
    "NIFTY_INDIA_MFG.NS": "NSE:NIFTY_INDIA_MFG",
    "NIFTY_CAPITAL_MKT.NS": "NSE:NIFTY_CAPITAL_MKT",
    "NIFTY_CHEMICALS.NS": "NSE:NIFTY_CHEMICALS",
    "NIFTY_HOUSING.NS": "NSE:NIFTY_HOUSING",
    "NIFTY_TRANS_LOGIS.NS": "NSE:NIFTY_TRANS_LOGIS",
}

DEFAULT_CUSTOM_STOCKS = [
    {"id": "1", "symbol": "RELIANCE.NS", "sector": "Energy & Oil"},
    {"id": "2", "symbol": "RELIANCE.NS", "sector": "Retail & Consumer"},
    {"id": "3", "symbol": "TCS.NS", "sector": "IT Services"},
    {"id": "4", "symbol": "HDFCBANK.NS", "sector": "Private Banks"},
    {"id": "5", "symbol": "INFY.NS", "sector": "IT Services"},
]


def normalize_ticker(raw_symbol: str) -> str:
    sym = str(raw_symbol).strip().upper()
    if not sym:
        return ""
    if not sym.startswith("^") and "." not in sym and "=" not in sym:
        return f"{sym}.NS"
    return sym


def build_tradingview_url(ticker: str) -> str:
    clean = str(ticker).strip().upper()
    if clean in TV_SYMBOL_OVERRIDES:
        tv_sym = TV_SYMBOL_OVERRIDES[clean]
    elif clean.endswith(".NS"):
        tv_sym = f"NSE:{clean[:-3]}"
    elif clean.endswith(".BO"):
        tv_sym = f"BSE:{clean[:-3]}"
    else:
        tv_sym = f"NSE:{clean.lstrip('^')}"
    return f"https://www.tradingview.com/chart/?symbol={quote(tv_sym, safe=':')}"


def load_custom_stocks():
    if os.path.exists(CUSTOM_STOCKS_FILE):
        try:
            with open(CUSTOM_STOCKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    cleaned = []
                    for item in data[:MAX_CUSTOM_ENTRIES]:
                        if isinstance(item, dict) and item.get("symbol"):
                            cleaned.append({
                                "id": str(item.get("id") or uuid.uuid4())[:8],
                                "symbol": normalize_ticker(item["symbol"]),
                                "sector": str(item.get("sector") or "Uncategorized").strip() or "Uncategorized",
                            })
                    return cleaned
        except Exception:
            pass
    return [item.copy() for item in DEFAULT_CUSTOM_STOCKS]


def save_custom_stocks(entries):
    with open(CUSTOM_STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(entries[:MAX_CUSTOM_ENTRIES], f, indent=2)


# ---------------------------------------------------------
# 2. DAILY 9:10 AM IST AUTO-RESET ENGINE
# ---------------------------------------------------------
def get_current_reset_anchor(now_ist: datetime):
    """Returns today's date if current IST time >= 9:10 AM, else yesterday's date."""
    if now_ist.time() >= DAILY_RESET_TIME:
        return now_ist.date()
    return (now_ist - timedelta(days=1)).date()


def check_daily_910_reset():
    now_ist = datetime.now(IST)
    active_anchor = get_current_reset_anchor(now_ist)

    if "last_auto_reset_date" not in st.session_state:
        st.session_state.last_auto_reset_date = active_anchor
        st.session_state.last_auto_reset_ts = None

    if "sectors" not in st.session_state:
        st.session_state.sectors = DEFAULT_SECTORS.copy()

    if "custom_stocks" not in st.session_state:
        st.session_state.custom_stocks = load_custom_stocks()

    # Trigger reset once when crossing 9:10 AM IST on a new day
    if st.session_state.last_auto_reset_date != active_anchor:
        st.cache_data.clear()
        st.session_state.sectors = DEFAULT_SECTORS.copy()

        # Remove the next 2 lines if you want to keep your custom stock list across days
        st.session_state.custom_stocks = [item.copy() for item in DEFAULT_CUSTOM_STOCKS]
        save_custom_stocks(st.session_state.custom_stocks)

        st.session_state.last_auto_reset_date = active_anchor
        st.session_state.last_auto_reset_ts = now_ist.strftime("%d %b %Y, %I:%M:%S %p IST")


check_daily_910_reset()

# ---------------------------------------------------------
# 3. SIDEBAR: REFRESH, MANUAL RESET & SECTOR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Dashboard Controls")

    if st.button("🔄 Refresh Market Data Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    auto_refresh = st.toggle("Live Auto-Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", min_value=30, max_value=300, value=60, step=15)
    if auto_refresh:
        st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

    st.info("🕘 **Daily Auto-Reset:** Enabled for **9:10 AM IST** every day.")
    if st.session_state.get("last_auto_reset_ts"):
        st.caption(f"Last 9:10 AM reset ran: {st.session_state.last_auto_reset_ts}")

    st.divider()
    st.subheader("➕ Add Sector (Tab 1)")
    new_name = st.text_input("Sector Display Name", placeholder="e.g., NIFTY BANK")
    new_ticker = st.text_input("Yahoo Ticker", placeholder="e.g., ^NSEBANK")
    if st.button("Add Sector", use_container_width=True):
        if new_name and new_ticker:
            st.session_state.sectors[new_name.strip()] = new_ticker.strip()
            st.success(f"Added {new_name.strip()}")
            st.rerun()

    st.divider()
    st.subheader("🗑️ Remove / Reset Sectors (Tab 1)")
    to_remove = st.multiselect(
        "Select sectors to remove:",
        options=list(st.session_state.sectors.keys()),
    )
    if st.button("Remove Selected Sectors", use_container_width=True):
        for item in to_remove:
            del st.session_state.sectors[item]
        st.rerun()

    if st.button("Reset Default Sectors", use_container_width=True):
        st.session_state.sectors = DEFAULT_SECTORS.copy()
        st.rerun()


# ---------------------------------------------------------
# 4. MARKET METRICS ENGINE (SHARED BY SECTORS & STOCKS)
# ---------------------------------------------------------
def compute_metrics_for_ticker(df: pd.DataFrame):
    df = df.dropna(how="all")
    if df.empty or len(df) < 5:
        return None

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert(IST)
    else:
        df.index = df.index.tz_convert(IST)

    df = df.copy()
    df["Date"] = df.index.date
    unique_dates = sorted(df["Date"].unique())
    if len(unique_dates) < 2:
        return None

    today_date = unique_dates[-1]
    prev_date = unique_dates[-2]

    today_df = df[df["Date"] == today_date]
    prev_df = df[df["Date"] == prev_date]

    if today_df.empty or prev_df.empty:
        return None

    ltp = float(today_df["Close"].iloc[-1])
    prev_close = float(prev_df["Close"].iloc[-1])

    pdh = float(prev_df["High"].max())
    pdl = float(prev_df["Low"].min())

    orb_df = today_df.between_time(time(9, 15), time(9, 29))
    if not orb_df.empty:
        orb_high = float(orb_df["High"].max())
        orb_low = float(orb_df["Low"].min())
    else:
        orb_high = float(today_df["High"].iloc[0])
        orb_low = float(today_df["Low"].iloc[0])

    above_pdh = ltp > pdh
    below_pdl = ltp < pdl
    above_orb = ltp > orb_high
    below_orb = ltp < orb_low

    if above_pdh and above_orb:
        signal = SIGNAL_OPTIONS[0]
    elif below_pdl and below_orb:
        signal = SIGNAL_OPTIONS[1]
    elif above_pdh:
        signal = SIGNAL_OPTIONS[2]
    elif below_pdl:
        signal = SIGNAL_OPTIONS[3]
    elif above_orb:
        signal = SIGNAL_OPTIONS[4]
    elif below_orb:
        signal = SIGNAL_OPTIONS[5]
    else:
        signal = SIGNAL_OPTIONS[6]

    def pct_change_bars(bars_back: int) -> float:
        if len(df) > bars_back:
            past_price = float(df["Close"].iloc[-(bars_back + 1)])
            if past_price != 0:
                return ((ltp - past_price) / past_price) * 100
        return 0.0

    return {
        "LTP": round(ltp, 2),
        "Signal": signal,
        "PDH Status": "Above PDH" if above_pdh else ("Below PDL" if below_pdl else "Inside"),
        "15m ORB Status": "Above 15m H" if above_orb else ("Below 15m L" if below_orb else "Inside"),
        "Daily %": round(((ltp - prev_close) / prev_close) * 100, 2) if prev_close else 0.0,
        "5m %": round(pct_change_bars(1), 2),
        "10m %": round(pct_change_bars(2), 2),
        "15m %": round(pct_change_bars(3), 2),
        "30m %": round(pct_change_bars(6), 2),
        "1h %": round(pct_change_bars(12), 2),
        "4h %": round(pct_change_bars(48), 2),
        "PDH": round(pdh, 2),
        "PDL": round(pdl, 2),
        "15m High": round(orb_high, 2),
        "15m Low": round(orb_low, 2),
    }


@st.cache_data(ttl=55)
def fetch_batch_metrics(unique_tickers_tuple: tuple):
    tickers = list(unique_tickers_tuple)
    if not tickers:
        return {}

    raw_5m = yf.download(
        tickers=tickers,
        period="5d",
        interval="5m",
        group_by="ticker",
        progress=False,
        threads=True,
    )

    metrics_map = {}
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                df = raw_5m
            else:
                if ticker not in raw_5m.columns.get_level_values(0):
                    continue
                df = raw_5m[ticker]
            computed = compute_metrics_for_ticker(df)
            if computed:
                metrics_map[ticker] = computed
        except Exception:
            continue

    return metrics_map


def build_sectors_df(sector_dict: dict, metrics_map: dict) -> pd.DataFrame:
    rows = []
    for name, ticker in sector_dict.items():
        m = metrics_map.get(ticker)
        if m:
            rows.append({
                "Sector": name,
                "TV Chart": build_tradingview_url(ticker),
                "Ticker": ticker,
                **m,
            })
    return pd.DataFrame(rows)


def build_custom_stocks_df(entries: list, metrics_map: dict) -> pd.DataFrame:
    rows = []
    for item in entries:
        sym = item["symbol"]
        sec = item["sector"]
        m = metrics_map.get(sym)
        if m:
            rows.append({
                "Entry ID": item["id"],
                "Stock": sym,
                "TV Chart": build_tradingview_url(sym),
                "Sector": sec,
                **m,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------
# 5. TABLE RENDER HELPER (WITH TRADINGVIEW LINK COLUMN)
# ---------------------------------------------------------
PCT_COLS = ["Daily %", "5m %", "10m %", "15m %", "30m %", "1h %", "4h %"]
PRICE_COLS = ["LTP", "PDH", "PDL", "15m High", "15m Low"]


def render_scanner_table(df: pd.DataFrame, height: int = 600):
    column_config = {
        "TV Chart": st.column_config.LinkColumn(
            label="TradingView",
            display_text="Open Chart ↗",
        ),
    }
    for col in PRICE_COLS:
        if col in df.columns:
            column_config[col] = st.column_config.NumberColumn(col, format="%.2f")
    for col in PCT_COLS:
        if col in df.columns:
            column_config[col] = st.column_config.NumberColumn(col, format="%+.2f%%")

    st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        height=height,
        hide_index=True,
    )


def apply_signal_filter(df: pd.DataFrame, filter_choice: str) -> pd.DataFrame:
    if filter_choice == "All Signals":
        return df
    if filter_choice in SIGNAL_OPTIONS:
        return df[df["Signal"] == filter_choice]
    return df


# ---------------------------------------------------------
# 6. HEADER & SINGLE BATCH FETCH ACROSS BOTH TABS
# ---------------------------------------------------------
st.title("📊 Real-Time Sector & Stock Breakout Dashboard")
st.caption(
    f"Sectors: **{len(st.session_state.sectors)}** | "
    f"Custom Stock Entries: **{len(st.session_state.custom_stocks)}/{MAX_CUSTOM_ENTRIES}** | "
    f"Auto-Reset: **9:10 AM IST** | "
    f"Last Updated: **{datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p IST')}**"
)

all_unique_tickers = tuple(
    sorted(
        set(st.session_state.sectors.values())
        | {item["symbol"] for item in st.session_state.custom_stocks}
    )
)

with st.spinner("Fetching live Yahoo Finance 5m & intraday data..."):
    metrics_map = fetch_batch_metrics(all_unique_tickers)

tab1, tab2 = st.tabs([
    "🌐 Tab 1: Sector Breakout Scanner",
    f"🎯 Tab 2: Custom Stock Scanner ({len(st.session_state.custom_stocks)}/{MAX_CUSTOM_ENTRIES})",
])

# ---------------------------------------------------------
# 7. TAB 1: SECTOR BREAKOUT SCANNER
# ---------------------------------------------------------
with tab1:
    sector_df = build_sectors_df(st.session_state.sectors, metrics_map)

    if sector_df.empty:
        st.warning("No sector data available right now. Check ticker symbols or market hours.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🚀 Dual Bullish (PDH + 15m H)", int(sector_df["Signal"].str.contains("STRONG BULL").sum()))
        c2.metric("🔻 Dual Bearish (PDL + 15m L)", int(sector_df["Signal"].str.contains("STRONG BEAR").sum()))
        c3.metric("🟢 Above Prev Day High", int((sector_df["PDH Status"] == "Above PDH").sum()))
        c4.metric("🔴 Below Prev Day Low", int((sector_df["PDH Status"] == "Below PDL").sum()))

        t1_filter = st.radio(
            "Filter Sectors by Signal:",
            ["All Signals"] + SIGNAL_OPTIONS,
            horizontal=True,
            key="tab1_filter",
        )

        view_t1 = apply_signal_filter(sector_df, t1_filter).sort_values(by="Daily %", ascending=False).reset_index(drop=True)
        render_scanner_table(view_t1)

# ---------------------------------------------------------
# 8. TAB 2: CUSTOM STOCK SCANNER (UP TO 700 ENTRIES)
# ---------------------------------------------------------
with tab2:
    st.subheader("Manage Custom Stocks & Sectors (Same Stock Allowed in Multiple Sectors)")

    # Single Entry Form
    add_col1, add_col2, add_col3 = st.columns([2, 2, 1])
    with add_col1:
        inp_stock = st.text_input(
            "Stock Symbol",
            placeholder="e.g., RELIANCE or RELIANCE.NS",
            key="custom_stock_input",
        )
    with add_col2:
        inp_sector = st.text_input(
            "Sector Name (Any Name / Duplicates Allowed)",
            placeholder="e.g., Momentum Basket or Energy",
            key="custom_sector_input",
        )
    with add_col3:
        st.write("")
        st.write("")
        add_clicked = st.button("➕ Add Stock", use_container_width=True, key="btn_add_custom")

    if add_clicked:
        norm_sym = normalize_ticker(inp_stock)
        clean_sec = inp_sector.strip() if inp_sector.strip() else "Uncategorized"
        if not norm_sym:
            st.error("Please enter a valid stock symbol.")
        elif len(st.session_state.custom_stocks) >= MAX_CUSTOM_ENTRIES:
            st.error(f"Limit reached ({MAX_CUSTOM_ENTRIES} entries). Remove entries before adding more.")
        else:
            st.session_state.custom_stocks.append({
                "id": str(uuid.uuid4())[:8],
                "symbol": norm_sym,
                "sector": clean_sec,
            })
            save_custom_stocks(st.session_state.custom_stocks)
            st.success(f"Added **{norm_sym}** under sector **{clean_sec}**.")
            st.rerun()

    # Manual Reset Bar
    r_col1, r_col2, r_col3 = st.columns([1.5, 1.5, 3])
    with r_col1:
        if st.button("↩️ Reset to Default List", use_container_width=True, key="btn_reset_default_stocks"):
            st.session_state.custom_stocks = [item.copy() for item in DEFAULT_CUSTOM_STOCKS]
            save_custom_stocks(st.session_state.custom_stocks)
            st.success("Reset custom stock list to defaults.")
            st.rerun()
    with r_col2:
        if st.button("🧹 Clear All Custom Stocks", use_container_width=True, key="btn_clear_all_stocks"):
            st.session_state.custom_stocks = []
            save_custom_stocks(st.session_state.custom_stocks)
            st.warning("Cleared all custom stock entries.")
            st.rerun()

    # Bulk Paste Expander
    with st.expander("📥 Bulk Add Stocks (Paste `STOCK, SECTOR` One Per Line — Up to 700 Total)"):
        st.caption("Example:\n`INFY, IT Sector`\n`INFY, High Beta`\n`HDFCBANK, Banking`")
        bulk_text = st.text_area("Paste rows here:", height=120, key="bulk_stocks_area")
        if st.button("Import Bulk List", key="btn_bulk_import"):
            added_count = 0
            for line in bulk_text.splitlines():
                if len(st.session_state.custom_stocks) >= MAX_CUSTOM_ENTRIES:
                    break
                parts = [p.strip() for p in line.split(",", 1)]
                sym = normalize_ticker(parts[0]) if parts and parts[0] else ""
                sec = parts[1] if len(parts) > 1 and parts[1] else "Uncategorized"
                if sym:
                    st.session_state.custom_stocks.append({
                        "id": str(uuid.uuid4())[:8],
                        "symbol": sym,
                        "sector": sec,
                    })
                    added_count += 1
            save_custom_stocks(st.session_state.custom_stocks)
            st.success(f"Imported {added_count} stock-sector rows.")
            st.rerun()

    # CSV / JSON Export & Import Expander
    with st.expander("💾 Export & Import Custom Stock List (CSV / JSON)"):
        ex_col1, ex_col2 = st.columns(2)

        export_df = pd.DataFrame(st.session_state.custom_stocks)
        if export_df.empty:
            export_df = pd.DataFrame(columns=["id", "symbol", "sector"])

        with ex_col1:
            csv_data = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Export List as CSV",
                data=csv_data,
                file_name="custom_stocks_700.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_export_csv",
            )

        with ex_col2:
            json_data = json.dumps(st.session_state.custom_stocks, indent=2).encode("utf-8")
            st.download_button(
                label="⬇️ Export List as JSON",
                data=json_data,
                file_name="custom_stocks_700.json",
                mime="application/json",
                use_container_width=True,
                key="btn_export_json",
            )

        st.divider()
        import_mode = st.radio(
            "When importing a file:",
            ["Append to existing list (up to 700)", "Replace existing list"],
            horizontal=True,
            key="import_mode_radio",
        )
        uploaded_file = st.file_uploader(
            "Upload CSV or JSON file (CSV needs `symbol` and `sector` columns)",
            type=["csv", "json"],
            key="custom_stocks_uploader",
        )

        if uploaded_file is not None and st.button("📤 Import Uploaded File", key="btn_import_file"):
            imported_rows = []
            try:
                if uploaded_file.name.lower().endswith(".json"):
                    raw_json = json.load(uploaded_file)
                    if isinstance(raw_json, list):
                        for item in raw_json:
                            if isinstance(item, dict) and item.get("symbol"):
                                sym = normalize_ticker(item["symbol"])
                                sec = str(item.get("sector") or "Uncategorized").strip() or "Uncategorized"
                                if sym:
                                    imported_rows.append({
                                        "id": str(uuid.uuid4())[:8],
                                        "symbol": sym,
                                        "sector": sec,
                                    })
                elif uploaded_file.name.lower().endswith(".csv"):
                    content = uploaded_file.getvalue().decode("utf-8")
                    imp_df = pd.read_csv(StringIO(content))
                    cols_lower = {c.lower().strip(): c for c in imp_df.columns}
                    sym_col = cols_lower.get("symbol") or cols_lower.get("stock") or cols_lower.get("ticker")
                    sec_col = cols_lower.get("sector")
                    if not sym_col:
                        st.error("CSV must contain a 'symbol', 'stock', or 'ticker' column.")
                    else:
                        for _, row in imp_df.iterrows():
                            sym = normalize_ticker(row[sym_col])
                            sec = str(row[sec_col]).strip() if sec_col and pd.notna(row[sec_col]) and str(row[sec_col]).strip() else "Uncategorized"
                            if sym:
                                imported_rows.append({
                                    "id": str(uuid.uuid4())[:8],
                                    "symbol": sym,
                                    "sector": sec,
                                })

                if imported_rows:
                    if import_mode.startswith("Replace"):
                        updated = imported_rows[:MAX_CUSTOM_ENTRIES]
                    else:
                        remaining_slots = max(0, MAX_CUSTOM_ENTRIES - len(st.session_state.custom_stocks))
                        updated = st.session_state.custom_stocks + imported_rows[:remaining_slots]

                    st.session_state.custom_stocks = updated
                    save_custom_stocks(st.session_state.custom_stocks)
                    st.success(f"Imported {len(imported_rows)} rows. Total entries: {len(st.session_state.custom_stocks)}/{MAX_CUSTOM_ENTRIES}.")
                    st.rerun()
            except Exception as e:
                st.error(f"Could not import file: {e}")

    st.divider()

    stock_df = build_custom_stocks_df(st.session_state.custom_stocks, metrics_map)

    if stock_df.empty:
        st.info("No custom stock data displayed yet. Add stocks above or import a CSV/JSON file.")
    else:
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("🚀 Dual Bullish", int(stock_df["Signal"].str.contains("STRONG BULL").sum()))
        sc2.metric("🔻 Dual Bearish", int(stock_df["Signal"].str.contains("STRONG BEAR").sum()))
        sc3.metric("🟢 Above PDH", int((stock_df["PDH Status"] == "Above PDH").sum()))
        sc4.metric("🔴 Below PDL", int((stock_df["PDH Status"] == "Below PDL").sum()))

        f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
        with f_col1:
            available_sectors = ["All Sectors"] + sorted(stock_df["Sector"].unique().tolist())
            selected_sec_filter = st.selectbox("Filter by Sector:", available_sectors, key="tab2_sec_filter")
        with f_col2:
            present_signals = [opt for opt in SIGNAL_OPTIONS if opt in stock_df["Signal"].unique()]
            signal_filter_choices = ["All Signals"] + present_signals
            selected_sig_filter = st.selectbox(
                "Filter by Breakout / Signal:",
                signal_filter_choices,
                key="tab2_sig_filter",
            )
        with f_col3:
            search_stock = st.text_input("Search Stock Symbol:", placeholder="e.g., RELIANCE", key="tab2_search")

        view_t2 = stock_df.copy()
        if selected_sec_filter != "All Sectors":
            view_t2 = view_t2[view_t2["Sector"] == selected_sec_filter]
        if selected_sig_filter != "All Signals":
            view_t2 = view_t2[view_t2["Signal"] == selected_sig_filter]
        if search_stock.strip():
            q = search_stock.strip().upper()
            view_t2 = view_t2[view_t2["Stock"].str.upper().str.contains(q, na=False)]

        view_t2 = view_t2.sort_values(by="Daily %", ascending=False).reset_index(drop=True)
        render_scanner_table(view_t2.drop(columns=["Entry ID"]), height=550)

        with st.expander("🗑️ Remove Specific Stock-Sector Entries"):
            entry_labels = {
                f"[{row['Entry ID']}] {row['Stock']} → {row['Sector']}": row["Entry ID"]
                for _, row in stock_df.iterrows()
            }
            selected_to_delete = st.multiselect(
                "Select entries to remove:",
                options=list(entry_labels.keys()),
                key="delete_custom_entries",
            )
            if st.button("Remove Selected Stock Entries", key="btn_delete_custom"):
                ids_to_del = {entry_labels[k] for k in selected_to_delete}
                st.session_state.custom_stocks = [
                    x for x in st.session_state.custom_stocks if x["id"] not in ids_to_del
                ]
                save_custom_stocks(st.session_state.custom_stocks)
                st.rerun()
