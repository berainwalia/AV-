import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query, Column
from streamlit_autorefresh import st_autorefresh
import threading
import time as time_module

# ==========================================
# CONFIGURATION & SECTOR MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

SECTOR_INDEX_MAP = {
    "360ONE": "NIFTY Fin Service", "ABB": "NIFTY Energy", "ABBOTINDIA": "NIFTY Pharma",
    "ABCAPITAL": "NIFTY Fin Service", "ABSLAMC": "NIFTY Fin Service", "ADANIENSOL": "NIFTY Energy",
    "ADANIENT": "NIFTY Metal", "ADANIGREEN": "NIFTY Infra", "ADANIPORTS": "NIFTY Infra",
    "ADANIPOWER": "NIFTY Energy", "AEQUS": "NIFTY Defence", "AJANTPHARM": "NIFTY Pharma",
    "ALKEM": "NIFTY Healthcare", "AMBER": "NIFTY Consumer Durables", "AMBUJACEM": "NIFTY Infra",
    "ANANDRATHI": "NIFTY Fin Service", "ANGELONE": "NIFTY Fin Service", "APLAPOLLO": "NIFTY Metal",
    "APOLLOHOSP": "NIFTY Healthcare", "ASHOKLEY": "NIFTY Auto", "ASIANPAINT": "NIFTY Consumption",
    "ASTRAL": "NIFTY Plastics", "AUBANK": "NIFTY Bank", "AUROPHARMA": "NIFTY Healthcare",
    "AXISBANK": "NIFTY Bank", "AXISCADES": "NIFTY Defence", "BAJAJ-AUTO": "NIFTY Auto",
    "BAJAJFINSV": "NIFTY Fin Service", "BAJAJHLDNG": "NIFTY Fin Service", "BAJFINANCE": "NIFTY Fin Service",
    "BANDHANBNK": "NIFTY Bank", "BANKBARODA": "NIFTY PSU Bank", "BANKINDIA": "NIFTY PSU Bank",
    "BDL": "NIFTY Defence", "BEL": "NIFTY Defence", "BHARATFORG": "NIFTY Auto",
    "BHARTIARTL": "NIFTY Infra", "BHEL": "NIFTY Energy", "BIOCON": "NIFTY Healthcare",
    "BLUESTARCO": "NIFTY Consumer Durables", "BOSCHLTD": "NIFTY Auto", "BPCL": "NIFTY Oil & Gas",
    "BRITANNIA": "NIFTY FMCG", "BSE": "NIFTY Fin Service", "CAMS": "NIFTY Fin Service",
    "CANBK": "NIFTY PSU Bank", "CDSL": "NIFTY Fin Service", "CGPOWER": "NIFTY Infra",
    "CHOLAFIN": "NIFTY Fin Service", "CIPLA": "NIFTY Healthcare", "COALINDIA": "NIFTY Energy",
    "COCHINSHIP": "NIFTY Defence", "COFORGE": "NIFTY IT", "COLPAL": "NIFTY FMCG",
    "CONCOR": "NIFTY Transportation", "CROMPTON": "NIFTY Consumer Durables", "CUMMINSIN": "NIFTY Infra",
    "CUMMINSIND": "NIFTY Infra", "DABUR": "NIFTY FMCG", "DALBHARAT": "NIFTY Infra",
    "DELHIVERY": "NIFTY Transportation", "DIVISLAB": "NIFTY Healthcare", "DIXON": "NIFTY Consumer Durables",
    "DLF": "NIFTY Realty", "DMART": "NIFTY Consumer Durables", "DRREDDY": "NIFTY Healthcare",
    "EICHERMOT": "NIFTY Auto", "ETERNAL": "NIFTY Services", "EXIDEIND": "NIFTY Auto",
    "FEDERALBNK": "NIFTY Bank", "FORCEMOT": "NIFTY Auto", "FORTIS": "NIFTY Healthcare",
    "GAIL": "NIFTY Oil & Gas", "GLAND": "NIFTY Pharma", "GLENMARK": "NIFTY Healthcare",
    "GMRAIRPORT": "NIFTY Infra", "GODFRYPHLP": "NIFTY FMCG", "GODREJCP": "NIFTY FMCG",
    "GODREJPROP": "NIFTY Realty", "GRASIM": "NIFTY Infra", "GROWW": "NIFTY Fin Service",
    "GVT&D": "NIFTY Energy", "HAL": "NIFTY Defence", "HAVELLS": "NIFTY Consumer Durables",
    "HCLTECH": "NIFTY IT", "HDFCAMC": "NIFTY Fin Service", "HDFCBANK": "NIFTY Bank",
    "HDFCLIFE": "NIFTY Fin Service", "HEROMOTOCO": "NIFTY Auto", "HINDALCO": "NIFTY Metal",
    "HINDPETRO": "NIFTY Oil & Gas", "HINDUNILVR": "NIFTY FMCG", "HINDZINC": "NIFTY Metal",
    "HYUNDAI": "NIFTY Auto", "ICICIAMC": "NIFTY Fin Service", "ICICIBANK": "NIFTY Bank",
    "ICICIGI": "NIFTY Fin Service", "ICICIPRULI": "NIFTY Fin Service", "IDEA": "NIFTY Telecom",
    "IDFCFIRSTB": "NIFTY Bank", "IEX": "NIFTY Fin Service", "INDHOTEL": "NIFTY Infra",
    "INDIANB": "NIFTY PSU Bank", "INDIGO": "NIFTY Infra", "INDUSINDBK": "NIFTY Bank",
    "INDUSTOWER": "NIFTY Infra", "INFY": "NIFTY IT", "INOXWIND": "NIFTY Energy",
    "IOC": "NIFTY Oil & Gas", "IPCALAB": "NIFTY Pharma", "IREDA": "NIFTY Fin Service",
    "IRFC": "NIFTY Fin Service", "ITC": "NIFTY FMCG", "JBCHEPHARM": "NIFTY Pharma",
    "JINDALSTEL": "NIFTY Metal", "JIOFIN": "NIFTY Fin Service", "JSWENERGY": "NIFTY Energy",
    "JSWSTEEL": "NIFTY Metal", "JUBLFOOD": "NIFTY Consumer Durables", "KALYANKJIL": "NIFTY Consumer Durables",
    "KAYNES": "NIFTY Consumer Durables", "KEI": "NIFTY Industrials", "KFINTECH": "NIFTY Fin Service",
    "KOTAKBANK": "NIFTY Bank", "KPITTECH": "NIFTY IT", "LAURUSLABS": "NIFTY Healthcare",
    "LGEINDIA": "NIFTY Consumer Durables", "LICHSGFIN": "NIFTY Fin Service", "LICI": "NIFTY Fin Service",
    "LODHA": "NIFTY Realty", "LT": "NIFTY Infra", "LTF": "NIFTY Fin Service",
    "LTM": "NIFTY IT", "LUPIN": "NIFTY Healthcare", "M&M": "NIFTY Auto",
    "MANAPPURAM": "NIFTY Fin Service", "MANKIND": "NIFTY Healthcare", "MARICO": "NIFTY FMCG",
    "MARUTI": "NIFTY Auto", "MAXHEALTH": "NIFTY Healthcare", "MAZDOCK": "NIFTY Defence",
    "MCX": "NIFTY Fin Service", "MFSL": "NIFTY Fin Service", "MOTHERSON": "NIFTY Auto",
    "MOTILALOFS": "NIFTY Fin Service", "MPHASIS": "NIFTY IT", "MUTHOOTFIN": "NIFTY Fin Service",
    "NAM-INDIA": "NIFTY Fin Service", "NATIONALUM": "NIFTY Metal", "NAUKRI": "NIFTY IT",
    "NBCC": "NIFTY Realty", "NESTLEIND": "NIFTY FMCG", "NHPC": "NIFTY Energy",
    "NMDC": "NIFTY Metal", "NTPC": "NIFTY Infra", "NUVAMA": "NIFTY Fin Service",
    "NYKAA": "NIFTY IT", "OBEROIRLTY": "NIFTY Realty", "OFSS": "NIFTY IT",
    "OIL": "NIFTY Oil & Gas", "ONGC": "NIFTY Oil & Gas", "PAGEIND": "NIFTY Consumer Durables",
    "PATANJALI": "NIFTY FMCG", "PAYTM": "NIFTY Fin Service", "PERSISTENT": "NIFTY IT",
    "PETRONET": "NIFTY Oil & Gas", "PFC": "NIFTY Fin Service", "PGEL": "NIFTY Consumer Durables",
    "PHOENIXLTD": "NIFTY Realty", "PIDILITIND": "NIFTY Chemicals", "PIIND": "NIFTY Chemicals",
    "PNB": "NIFTY PSU Bank", "PNBHOUSING": "NIFTY Fin Service", "POLICYBZR": "NIFTY Fin Service",
    "POLYCAB": "NIFTY Industrials", "POWERGRID": "NIFTY Infra", "POWERINDIA": "NIFTY Energy",
    "PREMIERENE": "NIFTY Services", "PRESTIGE": "NIFTY Realty", "RADICO": "NIFTY FMCG",
    "RBLBANK": "NIFTY Bank", "RECLTD": "NIFTY Fin Service", "RELIANCE": "NIFTY Oil & Gas",
    "RVNL": "NIFTY Realty", "SAIL": "NIFTY Metal", "SBICARD": "NIFTY Fin Service",
    "SBILIFE": "NIFTY Fin Service", "SBIN": "NIFTY PSU Bank", "SHREECEM": "NIFTY Infra",
    "SHRIRAMFIN": "NIFTY Fin Service", "SIEMENS": "NIFTY Energy", "SOLARINDS": "NIFTY Defence",
    "SONACOMS": "NIFTY Auto", "SRF": "NIFTY Chemicals", "SUNPHARMA": "NIFTY Healthcare",
    "SUPREMEIND": "NIFTY Plastics", "SUZLON": "NIFTY Infra", "SWIGGY": "NIFTY Services",
    "TATACONSUM": "NIFTY FMCG", "TATAELXSI": "NIFTY IT", "TATAPOWER": "NIFTY Infra",
    "TATASTEEL": "NIFTY Metal", "TCS": "NIFTY IT", "TECHM": "NIFTY IT",
    "TIINDIA": "NIFTY Auto", "TITAN": "NIFTY Consumer Durables", "TMPV": "NIFTY Auto",
    "TORNTPHARM": "NIFTY Healthcare", "TRENT": "NIFTY Consumer Durables", "TVSMOTOR": "NIFTY Auto",
    "ULTRACEMCO": "NIFTY Infra", "UNIMECH": "NIFTY Defence", "UNIONBANK": "NIFTY PSU Bank",
    "UNITDSPR": "NIFTY FMCG", "UNOMINDA": "NIFTY Auto", "UPL": "NIFTY Chemicals",
    "UTIAMC": "NIFTY Fin Service", "VBL": "NIFTY FMCG", "VEDL": "NIFTY Metal",
    "VMM": "NIFTY Consumer Durables", "VOLTAS": "NIFTY Consumer Durables", "WAAREEENER": "NIFTY Industrials",
    "WIPRO": "NIFTY IT", "WOCKPHARMA": "NIFTY Pharma", "YESBANK": "NIFTY Bank",
    "ZYDUSLIFE": "NIFTY Healthcare"
}

VALID_SYMBOLS = set(SECTOR_INDEX_MAP.keys())

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

# UI Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="datarefresh")

# ==========================================
# DATABASE FUNCTIONS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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
        (now_str, row['Symbol'], float(row['RelVol']), float(row['ChangePct']), str(row['Sector Index'])) 
        for _, row in df.iterrows()
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO relvol_snapshots (timestamp, symbol, rel_vol, change_pct, sector_index) 
        VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

# ==========================================
# DYNAMIC SCANNER FETCHING
# ==========================================
def fetch_live_fno_data(stock_universe_mode="Custom List"):
    try:
        limit = 200 if stock_universe_mode == "Custom List" else (250 if stock_universe_mode == "All F&O Stocks" else 500)
        
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
        print(f"Error pulling stock updates: {e}")
        return pd.DataFrame()

# ==========================================
# BACKGROUND AUTOMATIC SNAPSHOT SCHEDULER
# ==========================================
def auto_snapshot_loop():
    """Takes background snapshots every 60 seconds independent of web UI status."""
    while True:
        try:
            now_dt = datetime.now(TIMEZONE)
            if now_dt.weekday() < 5:
                curr_time = now_dt.time()
                if time(9, 15) <= curr_time <= time(15, 30):
                    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
                    today_date_str = now_dt.strftime("%Y-%m-%d")
                    
                    check_and_reset_daily(today_date_str)
                    
                    df = fetch_live_fno_data("All F&O Stocks")
                    if not df.empty:
                        save_snapshot(df, now_str)
        except Exception as e:
            print(f"Background Snapshot Exception: {e}")
            
        time_module.sleep(60)

init_db()

if "bg_thread_started" not in st.session_state:
    st.session_state["bg_thread_started"] = True
    bg_thread = threading.Thread(target=auto_snapshot_loop, daemon=True)
    bg_thread.start()

# ==========================================
# CALCULATIONS & PROCESSING
# ==========================================
def calculate_gain_by_exact_timestamps(start_ts, end_ts, label_name="Gain"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (end_ts,))
    end_row = cursor.fetchone()
    
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (start_ts,))
    start_row = cursor.fetchone()

    if not end_row or not start_row or not end_row[0] or not start_row[0]:
        conn.close()
        return pd.DataFrame(), label_name, None, None

    actual_start_ts = start_row[0]
    actual_end_ts = end_row[0]

    df_end = pd.read_sql_query("SELECT symbol, rel_vol, change_pct, sector_index FROM relvol_snapshots WHERE timestamp = ?", conn, params=(actual_end_ts,))
    df_start = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(actual_start_ts,))
    conn.close()

    if df_end.empty or df_start.empty:
        return pd.DataFrame(), label_name, actual_start_ts, actual_end_ts

    merged = pd.merge(df_end, df_start, on='symbol', suffixes=('_end', '_start'))
    merged['Gain'] = merged['rel_vol_end'] - merged['rel_vol_start']

    top = merged.sort_values(by='Gain', ascending=False).head(20).copy()
    top['TradingView Chart'] = top['symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    top = top[['symbol', 'sector_index', 'TradingView Chart', 'change_pct', 'rel_vol_end', 'Gain']].copy()
    top['rel_vol_end'] = top['rel_vol_end'].round(2)
    top['Gain'] = top['Gain'].round(2)
    top['change_pct'] = top['change_pct'].round(2)

    top.columns = ['Symbol', 'Sector Index', 'TradingView Chart', 'Price Change %', 'End Rel Vol', label_name]
    return top.reset_index(drop=True), label_name, actual_start_ts, actual_end_ts

def calculate_gain_relative(minutes, current_time_str):
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    start_str = (curr_dt - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    df, label, _, _ = calculate_gain_by_exact_timestamps(start_str, current_time_str, f'+{minutes}m Gain')
    return df, label

def fetch_day_movers_with_multi_timeframes(live_df, current_time_str):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame()

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
    df['TradingView Chart'] = df['Symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    df['+1m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_1m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+3m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_3m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+5m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_5m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+10m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_10m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+15m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_15m.get(r['Symbol'], r['RelVol']), 2), axis=1)

    df['RelVol'] = df['RelVol'].round(2)
    df['ChangePct'] = df['ChangePct'].round(2)

    gainers = df.sort_values(by='ChangePct', ascending=False).head(20).copy()
    losers = df.sort_values(by='ChangePct', ascending=True).head(20).copy()

    cols_order = [
        'Symbol', 'Sector Index', 'TradingView Chart', 'ChangePct', 
        'RelVol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain'
    ]
    col_names = [
        'Stock Symbol', 'Sector Index', 'Chart Link', 'Price Change (%)', 
        'End Rel Vol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain'
    ]

    if not gainers.empty:
        gainers = gainers[cols_order]
        gainers.columns = col_names

    if not losers.empty:
        losers = losers[cols_order]
        losers.columns = col_names

    return gainers.reset_index(drop=True), losers.reset_index(drop=True)

# ==========================================
# NEW: SECTOR MAPPING & HEATMAP FUNCTIONALITY
# ==========================================
def fetch_sector_momentum_summary(live_df, current_time_str):
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
    vol_15m = get_past_relvol(15)
    conn.close()

    df = live_df.copy()
    df['+1m Gain'] = df.apply(lambda r: r['RelVol'] - vol_1m.get(r['Symbol'], r['RelVol']), axis=1)
    df['+3m Gain'] = df.apply(lambda r: r['RelVol'] - vol_3m.get(r['Symbol'], r['RelVol']), axis=1)
    df['+5m Gain'] = df.apply(lambda r: r['RelVol'] - vol_5m.get(r['Symbol'], r['RelVol']), axis=1)
    df['+15m Gain'] = df.apply(lambda r: r['RelVol'] - vol_15m.get(r['Symbol'], r['RelVol']), axis=1)
    df['Is Advance'] = df['ChangePct'] > 0

    # Sector-level Grouping & Summary Aggregation
    sector_summary = df.groupby('Sector Index').agg(
        Total_Stocks=('Symbol', 'count'),
        Advancing_Stocks=('Is Advance', 'sum'),
        Avg_Price_Change=('ChangePct', 'mean'),
        Avg_Rel_Vol=('RelVol', 'mean'),
        Avg_1m_Gain=('+1m Gain', 'mean'),
        Avg_3m_Gain=('+3m Gain', 'mean'),
        Avg_5m_Gain=('+5m Gain', 'mean'),
        Avg_15m_Gain=('+15m Gain', 'mean')
    ).reset_index()

    sector_summary['Declining_Stocks'] = sector_summary['Total_Stocks'] - sector_summary['Advancing_Stocks']
    sector_summary['Breadth Ratio (A/D)'] = sector_summary.apply(
        lambda r: f"{int(r['Advancing_Stocks'])} : {int(r['Declining_Stocks'])}", axis=1
    )

    # Formatting and rounding
    sector_summary['Avg Price Change (%)'] = sector_summary['Avg_Price_Change'].round(2)
    sector_summary['Avg Rel Vol'] = sector_summary['Avg_Rel_Vol'].round(2)
    sector_summary['+1m Vol Gain'] = sector_summary['Avg_1m_Gain'].round(2)
    sector_summary['+3m Vol Gain'] = sector_summary['Avg_3m_Gain'].round(2)
    sector_summary['+5m Vol Gain'] = sector_summary['Avg_5m_Gain'].round(2)
    sector_summary['+15m Vol Gain'] = sector_summary['Avg_15m_Gain'].round(2)

    sector_summary = sector_summary.sort_values(by='Avg Price Change (%)', ascending=False)

    cols = [
        'Sector Index', 'Total_Stocks', 'Breadth Ratio (A/D)', 'Avg Price Change (%)', 
        'Avg Rel Vol', '+1m Vol Gain', '+3m Vol Gain', '+5m Vol Gain', '+15m Vol Gain'
    ]
    return sector_summary[cols].reset_index(drop=True)

def fetch_sector_wise_data(live_df, current_time_str):
    if live_df.empty:
        return {}

    conn = sqlite3.connect(DB_NAME)
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (current_time_str,))
    latest_row = cursor.fetchone()

    if not latest_row:
        conn.close()
        return {}

    latest_ts = latest_row[0]
    base_df = pd.read_sql_query("SELECT symbol, rel_vol, change_pct, sector_index FROM relvol_snapshots WHERE timestamp = ?", conn, params=(latest_ts,))

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
    vol_15m = get_past_relvol(15)
    conn.close()

    base_df['Chart Link'] = base_df['symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")
    base_df['+1m Gain'] = base_df.apply(lambda r: round(r['rel_vol'] - vol_1m.get(r['symbol'], r['rel_vol']), 2), axis=1)
    base_df['+3m Gain'] = base_df.apply(lambda r: round(r['rel_vol'] - vol_3m.get(r['symbol'], r['rel_vol']), 2), axis=1)
    base_df['+5m Gain'] = base_df.apply(lambda r: round(r['rel_vol'] - vol_5m.get(r['symbol'], r['rel_vol']), 2), axis=1)
    base_df['+15m Gain'] = base_df.apply(lambda r: round(r['rel_vol'] - vol_15m.get(r['symbol'], r['rel_vol']), 2), axis=1)

    base_df['change_pct'] = base_df['change_pct'].round(2)
    base_df['rel_vol'] = base_df['rel_vol'].round(2)

    base_df = base_df.rename(columns={
        'symbol': 'Stock Symbol',
        'change_pct': 'Price Change (%)',
        'rel_vol': 'End Relative Volume (Rel Vol)',
        'sector_index': 'Sector'
    })

    cols = ['Stock Symbol', 'Chart Link', 'Price Change (%)', 'End Relative Volume (Rel Vol)', '+1m Gain', '+3m Gain', '+5m Gain', '+15m Gain']

    sector_tables = {}
    grouped = base_df.groupby('Sector')
    for sector, group in grouped:
        sector_tables[sector] = group[cols].sort_values(by='Price Change (%)', ascending=False).reset_index(drop=True)

    return sector_tables

def style_price_change(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: #00c853; font-weight: bold;'
        elif val < 0:
            return 'color: #ff1744; font-weight: bold;'
    return ''

def generate_5min_time_options():
    time_options = []
    today_date = datetime.now(TIMEZONE).date()
    
    start = datetime.combine(today_date, time(9, 15))
    end = datetime.combine(today_date, time(15, 30))
    
    current = start
    while current <= end:
        label = current.strftime('%I:%M %p')
        time_options.append((label, current.time()))
        current += timedelta(minutes=5)
    return time_options

# ==========================================
# DASHBOARD UI
# ==========================================
now_dt = datetime.now(TIMEZONE)
now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now_dt.strftime("%Y-%m-%d")

# Sidebar Configuration
st.sidebar.header("📌 Stock Universe Selection")
stock_universe_mode = st.sidebar.selectbox(
    "Choose Stock Universe:",
    options=["Custom List", "All F&O Stocks", "NIFTY 500 / All NSE Stocks"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Custom Time Range")

time_options = generate_5min_time_options()
time_labels = [opt[0] for opt in time_options]

selected_start_label = st.sidebar.selectbox(
    "Select Start Time:",
    options=time_labels,
    index=0
)

start_idx = time_labels.index(selected_start_label)
default_end_idx = min(start_idx + 1, len(time_labels) - 1)

selected_end_label = st.sidebar.selectbox(
    "Select End Time:",
    options=time_labels,
    index=default_end_idx
)

custom_start_time = next(opt[1] for opt in time_options if opt[0] == selected_start_label)
custom_end_time = next(opt[1] for opt in time_options if opt[0] == selected_end_label)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Snapshot History"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relvol_snapshots")
    conn.commit()
    conn.close()
    st.sidebar.success("Database reset successful!")
    st.rerun()

# Fetch UI Data
live_df = fetch_live_fno_data(stock_universe_mode)

st.title("⚡ NSE Relative Volume & Price Movers")
st.caption(f"Active Universe: **{stock_universe_mode} ({len(live_df)} Tickers)** | Background Worker Status: 🟢 **Active (1m Auto-Snapshots)** | Last refreshed: {now_str} IST")

# Timeframe & Analysis Tabs
tab_sector_leaderboard, tab1, tab3, tab5, tab10, tab15, tab_custom, tab_day, tab_sector_stocks = st.tabs([
    "🏛️ Sector Momentum", "1 Min", "3 Min", "5 Min", "10 Min", "15 Min", "🎯 Custom Range", "🔥 Top Gainers/Losers", "📊 Sector Stock Drilldown"
])

# Sector Momentum Leaderboard Tab
with tab_sector_leaderboard:
    st.subheader("🏛️ Sector & Thematic Momentum Summary")
    st.caption("Compare leading and lagging sectors across timeframes (+1m, +3m, +5m, +15m, and Daily % Change).")
    
    sector_summary_df = fetch_sector_momentum_summary(live_df, now_str)
    
    if not sector_summary_df.empty:
        styled_sec_summary = sector_summary_df.style.map(style_price_change, subset=['Avg Price Change (%)']).format({'Avg Price Change (%)': '{:+.2f}%'})
        st.dataframe(
            styled_sec_summary,
            use_container_width=True,
            column_config={
                "Sector Index": st.column_config.Column(alignment="center"),
                "Total_Stocks": st.column_config.Column("Total Stocks", alignment="center"),
                "Breadth Ratio (A/D)": st.column_config.Column("Breadth (Advances : Declines)", alignment="center"),
                "Avg Price Change (%)": st.column_config.Column(alignment="center"),
                "Avg Rel Vol": st.column_config.Column(alignment="center"),
                "+1m Vol Gain": st.column_config.Column(alignment="center"),
                "+3m Vol Gain": st.column_config.Column(alignment="center"),
                "+5m Vol Gain": st.column_config.Column(alignment="center"),
                "+15m Vol Gain": st.column_config.Column(alignment="center"),
            }
        )
    else:
        st.info("Accumulating sector snapshot data... Please wait a few moments.")

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 20 Volume Gainers - Last {mins} Minute(s)")
        df_gain, gain_col_name = calculate_gain_relative(mins, now_str)
        
        if not df_gain.empty:
            styled_df = df_gain.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "End Rel Vol": st.column_config.Column(alignment="center"),
                    gain_col_name: st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("Accumulating minute-by-minute background snapshots... Please wait a few moments.")

# Custom Range Tab
with tab_custom:
    st.subheader(f"Top 20 RelVol Gainers: {selected_start_label} ➔ {selected_end_label}")
    
    if custom_start_time >= custom_end_time:
        st.warning("⚠️ Select an **End Time** strictly after the **Start Time**.")
    else:
        start_ts_str = f"{today_date_str} {custom_start_time.strftime('%H:%M:%S')}"
        end_ts_str = f"{today_date_str} {custom_end_time.strftime('%H:%M:%S')}"
        
        df_custom, gain_col_name, act_start, act_end = calculate_gain_by_exact_timestamps(
            start_ts_str, 
            end_ts_str, 
            label_name="Custom Window Gain"
        )
        
        if not df_custom.empty:
            st.caption(f"Data window active from `{act_start.split(' ')[1]}` to `{act_end.split(' ')[1]}`.")
            styled_custom = df_custom.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_custom, 
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "End Rel Vol": st.column_config.Column(alignment="center"),
                    gain_col_name: st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info(f"No snapshot data recorded between {selected_start_label} and {selected_end_label} yet.")

# Day Gainers / Losers Tab
with tab_day:
    st.subheader("🔥 Top 20 Day Gainers & Losers with Multi-Timeframe Volume Momentum")
    
    gainers_df, losers_df = fetch_day_movers_with_multi_timeframes(live_df, now_str)
    
    st.markdown("### 🟢 Top 20 Day Gainers (% Increase)")
    if not gainers_df.empty:
        styled_gainers = gainers_df.style.map(style_price_change, subset=['Price Change (%)']).format({'Price Change (%)': '{:+.2f}%'})
        st.dataframe(
            styled_gainers,
            use_container_width=True,
            column_config={
                "Stock Symbol": st.column_config.Column(alignment="center"),
                "Sector Index": st.column_config.Column(alignment="center"),
                "Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 Open Chart", alignment="center"),
                "Price Change (%)": st.column_config.Column(alignment="center"),
                "End Rel Vol": st.column_config.Column(alignment="center"),
                "+1m Gain": st.column_config.Column(alignment="center"),
                "+3m Gain": st.column_config.Column(alignment="center"),
                "+5m Gain": st.column_config.Column(alignment="center"),
                "+10m Gain": st.column_config.Column(alignment="center"),
                "+15m Gain": st.column_config.Column(alignment="center"),
            }
        )
    else:
        st.info("No day gainers available.")

    st.markdown("---")
    st.markdown("### 🔴 Top 20 Day Losers (% Drop)")
    if not losers_df.empty:
        styled_losers = losers_df.style.map(style_price_change, subset=['Price Change (%)']).format({'Price Change (%)': '{:+.2f}%'})
        st.dataframe(
            styled_losers,
            use_container_width=True,
            column_config={
                "Stock Symbol": st.column_config.Column(alignment="center"),
                "Sector Index": st.column_config.Column(alignment="center"),
                "Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 Open Chart", alignment="center"),
                "Price Change (%)": st.column_config.Column(alignment="center"),
                "End Rel Vol": st.column_config.Column(alignment="center"),
                "+1m Gain": st.column_config.Column(alignment="center"),
                "+3m Gain": st.column_config.Column(alignment="center"),
                "+5m Gain": st.column_config.Column(alignment="center"),
                "+10m Gain": st.column_config.Column(alignment="center"),
                "+15m Gain": st.column_config.Column(alignment="center"),
            }
        )
    else:
        st.info("No day losers available.")

# Sector Stock Drilldown Tab
with tab_sector_stocks:
    st.subheader("📊 Individual Sector Stock Breakdown")
    
    sector_tables = fetch_sector_wise_data(live_df, now_str)
    
    if sector_tables:
        for sector_name, sec_df in sorted(sector_tables.items()):
            with st.expander(f"📁 **{sector_name}** ({len(sec_df)} Stocks)", expanded=True):
                styled_sec = sec_df.style.map(style_price_change, subset=['Price Change (%)']).format({'Price Change (%)': '{:+.2f}%'})
                st.dataframe(
                    styled_sec,
                    use_container_width=True,
                    column_config={
                        "Stock Symbol": st.column_config.Column(alignment="center"),
                        "Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 Open Chart", alignment="center"),
                        "Price Change (%)": st.column_config.Column(alignment="center"),
                        "End Relative Volume (Rel Vol)": st.column_config.Column(alignment="center"),
                        "+1m Gain": st.column_config.Column(alignment="center"),
                        "+3m Gain": st.column_config.Column(alignment="center"),
                        "+5m Gain": st.column_config.Column(alignment="center"),
                        "+15m Gain": st.column_config.Column(alignment="center"),
                    }
                )
    else:
        st.info("Accumulating sector snapshot data... Please wait a few moments.")
