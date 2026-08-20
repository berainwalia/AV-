import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query
from streamlit_autorefresh import st_autorefresh
import threading
import time as time_module

# ==========================================
# CONFIGURATION & MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# List of major NSE Sectoral and Thematic Indices on TradingView
INDICES_MAP = {
    "NIFTY 50": "NIFTY",
    "NIFTY BANK": "BANKNIFTY",
    "NIFTY IT": "CNXIT",
    "NIFTY AUTO": "CNXAUTO",
    "NIFTY PHARMA": "CNXPHARMA",
    "NIFTY REALTY": "CNXREALTY",
    "NIFTY INFRA": "CNXINFRA",
    "NIFTY ENERGY": "CNXENERGY",
    "NIFTY METAL": "CNXMETAL",
    "NIFTY FMCG": "CNXFMCG",
    "NIFTY PSU BANK": "CNXPSUBANK",
    "NIFTY DEFENCE": "NIFTY_DEFENCE",
    "NIFTY CPSE": "CNXCPSE",
    "NIFTY COMMODITIES": "CNXCOMMODITIES",
    "NIFTY CONSUMPTION": "CNXCONSUMPTION",
    "NIFTY PSE": "CNXPSE"
}

SECTOR_INDEX_MAP = {
    "360ONE": "NIFTY Fin Service", "ABB": "NIFTY Energy", "ABBOTINDIA": "NIFTY Pharma",
    "ABCAPITAL": "NIFTY Fin Service", "ABSLAMC": "NIFTY Fin Service", "ADANIENSOL": "NIFTY Energy",
    "ADANIENT": "NIFTY Metal", "ADANIGREEN": "NIFTY Infra", "ADANIPORTS": "NIFTY Infra",
    "ADANIPOWER": "NIFTY Energy", "AJANTPHARM": "NIFTY Pharma", "ALKEM": "NIFTY Healthcare",
    "AMBER": "NIFTY Consumer Durables", "AMBUJACEM": "NIFTY Infra", "APLAPOLLO": "NIFTY Metal",
    "APOLLOHOSP": "NIFTY Healthcare", "ASHOKLEY": "NIFTY Auto", "ASIANPAINT": "NIFTY Consumption",
    "ASTRAL": "NIFTY Plastics", "AUBANK": "NIFTY Bank", "AUROPHARMA": "NIFTY Healthcare",
    "AXISBANK": "NIFTY Bank", "BAJAJ-AUTO": "NIFTY Auto", "BAJAJFINSV": "NIFTY Fin Service",
    "BAJFINANCE": "NIFTY Fin Service", "BANDHANBNK": "NIFTY Bank", "BANKBARODA": "NIFTY PSU Bank",
    "BANKINDIA": "NIFTY PSU Bank", "BDL": "NIFTY Defence", "BEL": "NIFTY Defence",
    "BHARATFORG": "NIFTY Auto", "BHARTIARTL": "NIFTY Infra", "BHEL": "NIFTY Energy",
    "BIOCON": "NIFTY Healthcare", "BPCL": "NIFTY Oil & Gas", "BRITANNIA": "NIFTY FMCG",
    "BSE": "NIFTY Fin Service", "CANBK": "NIFTY PSU Bank", "CIPLA": "NIFTY Healthcare",
    "COALINDIA": "NIFTY Energy", "COCHINSHIP": "NIFTY Defence", "COFORGE": "NIFTY IT",
    "COLPAL": "NIFTY FMCG", "CONCOR": "NIFTY Transportation", "DABUR": "NIFTY FMCG",
    "DIVISLAB": "NIFTY Healthcare", "DIXON": "NIFTY Consumer Durables", "DLF": "NIFTY Realty",
    "DRREDDY": "NIFTY Healthcare", "EICHERMOT": "NIFTY Auto", "FEDERALBNK": "NIFTY Bank",
    "GAIL": "NIFTY Oil & Gas", "GODREJCP": "NIFTY FMCG", "GODREJPROP": "NIFTY Realty",
    "GRASIM": "NIFTY Infra", "HAL": "NIFTY Defence", "HCLTECH": "NIFTY IT",
    "HDFCBANK": "NIFTY Bank", "HDFCLIFE": "NIFTY Fin Service", "HEROMOTOCO": "NIFTY Auto",
    "HINDALCO": "NIFTY Metal", "HINDPETRO": "NIFTY Oil & Gas", "HINDUNILVR": "NIFTY FMCG",
    "ICICIBANK": "NIFTY Bank", "ICICIGI": "NIFTY Fin Service", "IDFCFIRSTB": "NIFTY Bank",
    "INDHOTEL": "NIFTY Infra", "INDIGO": "NIFTY Infra", "INDUSINDBK": "NIFTY Bank",
    "INFY": "NIFTY IT", "IOC": "NIFTY Oil & Gas", "IRFC": "NIFTY Fin Service",
    "ITC": "NIFTY FMCG", "JINDALSTEL": "NIFTY Metal", "JIOFIN": "NIFTY Fin Service",
    "JSWSTEEL": "NIFTY Metal", "KOTAKBANK": "NIFTY Bank", "LT": "NIFTY Infra",
    "LTIM": "NIFTY IT", "LUPIN": "NIFTY Healthcare", "M&M": "NIFTY Auto",
    "MARICO": "NIFTY FMCG", "MARUTI": "NIFTY Auto", "MAXHEALTH": "NIFTY Healthcare",
    "MCX": "NIFTY Fin Service", "MPHASIS": "NIFTY IT", "MUTHOOTFIN": "NIFTY Fin Service",
    "NATIONALUM": "NIFTY Metal", "NAUKRI": "NIFTY IT", "NESTLEIND": "NIFTY FMCG",
    "NTPC": "NIFTY Infra", "ONGC": "NIFTY Oil & Gas", "PERSISTENT": "NIFTY IT",
    "PFC": "NIFTY Fin Service", "PIDILITIND": "NIFTY Chemicals", "PNB": "NIFTY PSU Bank",
    "POLYCAB": "NIFTY Industrials", "POWERGRID": "NIFTY Infra", "RECLTD": "NIFTY Fin Service",
    "RELIANCE": "NIFTY Oil & Gas", "SAIL": "NIFTY Metal", "SBICARD": "NIFTY Fin Service",
    "SBILIFE": "NIFTY Fin Service", "SBIN": "NIFTY PSU Bank", "SHRIRAMFIN": "NIFTY Fin Service",
    "SIEMENS": "NIFTY Energy", "SOLARINDS": "NIFTY Defence", "SUNPHARMA": "NIFTY Healthcare",
    "TATACONSUM": "NIFTY FMCG", "TATAMOTORS": "NIFTY Auto", "TATAPOWER": "NIFTY Infra",
    "TATASTEEL": "NIFTY Metal", "TCS": "NIFTY IT", "TECHM": "NIFTY IT",
    "TITAN": "NIFTY Consumer Durables", "TORNTPHARM": "NIFTY Healthcare", "TRENT": "NIFTY Consumer Durables",
    "TVSMOTOR": "NIFTY Auto", "ULTRACEMCO": "NIFTY Infra", "UNITDSPR": "NIFTY FMCG",
    "VBL": "NIFTY FMCG", "VEDL": "NIFTY Metal", "VOLTAS": "NIFTY Consumer Durables",
    "WIPRO": "NIFTY IT", "YESBANK": "NIFTY Bank", "ZYDUSLIFE": "NIFTY Healthcare"
}

VALID_SYMBOLS = set(SECTOR_INDEX_MAP.keys())

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

# UI Auto-refresh every 30 seconds
st_autorefresh(interval=30000, key="datarefresh")

# ==========================================
# DATABASE FUNCTIONS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relvol_snapshots (
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            rel_vol REAL NOT NULL,
            change_pct REAL,
            sector_index TEXT,
            PRIMARY KEY (timestamp, symbol)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def check_and_reset_daily(today_date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'last_reset_date'")
    row = cursor.fetchone()
    if not row or row[0] != today_date_str:
        cursor.execute("DELETE FROM relvol_snapshots")
        cursor.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('last_reset_date', ?)", (today_date_str,))
        conn.commit()
    conn.close()

def save_snapshot(df, now_str):
    if df.empty:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data = [
        (now_str, str(row['Symbol']), float(row['RelVol']), float(row['ChangePct']), str(row['Sector Index']))
        for _, row in df.iterrows()
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO relvol_snapshots (timestamp, symbol, rel_vol, change_pct, sector_index)
        VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

# ==========================================
# DYNAMIC SCANNER DATA FETCHING
# ==========================================
def fetch_live_fno_data(stock_universe_mode="Custom List"):
    try:
        limit = 200 if stock_universe_mode == "Custom List" else 500
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'sector')
            .limit(limit)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]
        if df is None or df.empty:
            return pd.DataFrame()

        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector']].dropna(subset=['name', 'relative_volume_10d_calc', 'change'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector']
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()

        if stock_universe_mode == "Custom List":
            df = df[df['Symbol'].isin(VALID_SYMBOLS)].copy()

        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        df['Sector Index'] = df['Symbol'].map(SECTOR_INDEX_MAP).fillna(df['TV Sector'].fillna("Other Sector"))
        
        return df.dropna(subset=['RelVol', 'ChangePct']).reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame()

def fetch_live_indices_data():
    """Fetches real-time market data for Sectoral and Thematic Indices."""
    try:
        index_tickers = list(INDICES_MAP.values())
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change')
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]
        if df is None or df.empty:
            return pd.DataFrame()

        df.columns = ['Symbol', 'RelVol', 'ChangePct']
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        
        # Filter for Sector/Thematic Indices
        df = df[df['Symbol'].isin(index_tickers)].copy()
        
        # Map back to readable display names
        rev_map = {v: k for k, v in INDICES_MAP.items()}
        df['Display Name'] = df['Symbol'].map(rev_map)
        df['Sector Index'] = "Sector/Thematic Index"
        df['Symbol'] = df['Display Name']
        
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        
        return df[['Symbol', 'RelVol', 'ChangePct', 'Sector Index']].dropna().reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

# ==========================================
# BACKGROUND AUTOMATIC SNAPSHOT LOOP
# ==========================================
def auto_snapshot_loop():
    while True:
        try:
            now_dt = datetime.now(TIMEZONE)
            if now_dt.weekday() < 5:
                curr_time = now_dt.time()
                if time(9, 15) <= curr_time <= time(15, 30):
                    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
                    today_date_str = now_dt.strftime("%Y-%m-%d")
                    check_and_reset_daily(today_date_str)

                    # Fetch both stock data and indices data
                    stocks_df = fetch_live_fno_data("All F&O Stocks")
                    indices_df = fetch_live_indices_data()

                    combined_df = pd.concat([stocks_df, indices_df], ignore_index=True)
                    if not combined_df.empty:
                        save_snapshot(combined_df, now_str)
        except Exception as e:
            print(f"Background Loop Exception: {e}")
        time_module.sleep(30)

init_db()
if "bg_thread_started" not in st.session_state:
    st.session_state["bg_thread_started"] = True
    bg_thread = threading.Thread(target=auto_snapshot_loop, daemon=True)
    bg_thread.start()

# ==========================================
# TIMEFRAME CALCULATIONS
# ==========================================
def fetch_multi_timeframe_gainers_losers(live_df, current_time_str):
    if live_df.empty:
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_NAME)
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()

    def get_past_relvol(mins):
        past_str = (curr_dt - timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (past_str,))
        p_row = cursor.fetchone()
        if p_row:
            p_df = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(p_row[0],))
            return dict(zip(p_df['symbol'], p_df['rel_vol']))
        return {}

    vol_1m = get_past_relvol(1)
    vol_3m = get_past_relvol(3)
    vol_5m = get_past_relvol(5)
    vol_10m = get_past_relvol(10)
    vol_15m = get_past_relvol(15)
    conn.close()

    df = live_df.copy()
    df['TradingView Chart'] = df['Symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s.replace(' ', '_')}")
    df['+1m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_1m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+3m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_3m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+5m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_5m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+10m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_10m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+15m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_15m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['RelVol'] = df['RelVol'].round(2)
    df['ChangePct'] = df['ChangePct'].round(2)

    cols_order = ['Symbol', 'Sector Index', 'TradingView Chart', 'ChangePct', 'RelVol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain']
    col_names = ['Index / Stock Symbol', 'Category', 'Chart Link', 'Price Change (%)', 'End Rel Vol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain']

    df = df[cols_order]
    df.columns = col_names
    return df.sort_values(by='Price Change (%)', ascending=False).reset_index(drop=True)

# ==========================================
# STREAMLIT UI LAYOUT
# ==========================================
st.title("⚡ NSE Real-time Relative Volume & Price Tracker")

stock_universe = st.radio("Choose Stock Universe:", ["Custom List", "All F&O Stocks"], horizontal=True)

live_stocks = fetch_live_fno_data(stock_universe)
live_indices = fetch_live_indices_data()
now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

tab1, tab2, tab3 = st.tabs([
    "🚀 Day Stocks Top Gainers/Losers", 
    "📈 Sector & Thematic Indices", 
    "📊 Aggregated Sector Heatmap"
])

with tab1:
    st.subheader("Live Stocks Overview (Multi-Timeframe Gains)")
    stocks_df = fetch_multi_timeframe_gainers_losers(live_stocks, now_str)
    if not stocks_df.empty:
        st.dataframe(
            stocks_df, 
            column_config={"Chart Link": st.column_config.LinkColumn("TradingView")}, 
            use_container_width=True
        )
    else:
        st.info("Loading live stock data...")

with tab2:
    st.subheader("📈 Sector & Thematic Indices Relative Volume & Price Tracker")
    indices_df = fetch_multi_timeframe_gainers_losers(live_indices, now_str)
    if not indices_df.empty:
        st.dataframe(
            indices_df, 
            column_config={"Chart Link": st.column_config.LinkColumn("TradingView")}, 
            use_container_width=True
        )
    else:
        st.info("Loading Sector & Thematic Indices data...")

with tab3:
    st.subheader("📊 Aggregated Sector Summary")
    if not live_stocks.empty:
        sector_summary = live_stocks.groupby('Sector Index').agg(
            Total_Stocks=('Symbol', 'count'),
            Avg_Price_Change=('ChangePct', 'mean'),
            Avg_Rel_Vol=('RelVol', 'mean')
        ).reset_index()
        sector_summary['Avg_Price_Change'] = sector_summary['Avg_Price_Change'].round(2)
        sector_summary['Avg_Rel_Vol'] = sector_summary['Avg_Rel_Vol'].round(2)
        st.dataframe(sector_summary.sort_values(by='Avg_Price_Change', ascending=False), use_container_width=True)
        
