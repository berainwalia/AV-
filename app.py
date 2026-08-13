import sqlite3
from datetime import datetime, time, timedelta
import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from tradingview_screener import Column, Query

# ==========================================
# CONFIGURATION & SECTOR MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Strict sector mapping generated directly from your target universe
SECTOR_INDEX_MAP = {
    "360ONE": "NIFTY Fin Service",
    "ABB": "NIFTY Energy",
    "ABBOTINDIA": "NIFTY Pharma",
    "ABCAPITAL": "NIFTY Fin Service",
    "ABSLAMC": "NIFTY Fin Service",
    "ADANIENSOL": "NIFTY Energy",
    "ADANIENT": "NIFTY Metal",
    "ADANIGREEN": "NIFTY Infra",
    "ADANIPORTS": "NIFTY Infra",
    "ADANIPOWER": "NIFTY Energy",
    "AEQUS": "NIFTY Defence",
    "AJANTPHARM": "NIFTY Pharma",
    "ALKEM": "NIFTY Healthcare",
    "AMBER": "NIFTY Consumer Durables",
    "AMBUJACEM": "NIFTY Infra",
    "ANANDRATHI": "NIFTY Fin Service",
    "ANGELONE": "NIFTY Fin Service",
    "APLAPOLLO": "NIFTY Metal",
    "APOLLOHOSP": "NIFTY Healthcare",
    "ASHOKLEY": "NIFTY Auto",
    "ASIANPAINT": "NIFTY Consumption",
    "ASTRAL": "NIFTY Plastics",
    "AUBANK": "NIFTY Bank",
    "AUROPHARMA": "NIFTY Healthcare",
    "AXISBANK": "NIFTY Bank",
    "AXISCADES": "NIFTY Defence",
    "BAJAJ-AUTO": "NIFTY Auto",
    "BAJAJFINSV": "NIFTY Fin Service",
    "BAJAJHLDNG": "NIFTY Fin Service",
    "BAJFINANCE": "NIFTY Fin Service",
    "BANDHANBNK": "NIFTY Bank",
    "BANKBARODA": "NIFTY PSU Bank",
    "BANKINDIA": "NIFTY PSU Bank",
    "BDL": "NIFTY Defence",
    "BEL": "NIFTY Defence",
    "BHARATFORG": "NIFTY Auto",
    "BHARTIARTL": "NIFTY Infra",
    "BHEL": "NIFTY Energy",
    "BIOCON": "NIFTY Healthcare",
    "BLUESTARCO": "NIFTY Consumer Durables",
    "BOSCHLTD": "NIFTY Auto",
    "BPCL": "NIFTY Oil & Gas",
    "BRITANNIA": "NIFTY FMCG",
    "BSE": "NIFTY Fin Service",
    "CAMS": "NIFTY Fin Service",
    "CANBK": "NIFTY PSU Bank",
    "CDSL": "NIFTY Fin Service",
    "CGPOWER": "NIFTY Infra",
    "CHOLAFIN": "NIFTY Fin Service",
    "CIPLA": "NIFTY Healthcare",
    "COALINDIA": "NIFTY Energy",
    "COCHINSHIP": "NIFTY Defence",
    "COFORGE": "NIFTY IT",
    "COLPAL": "NIFTY FMCG",
    "CONCOR": "NIFTY Transportation",
    "CROMPTON": "NIFTY Consumer Durables",
    "CUMMINSIN": "NIFTY Infra",
    "CUMMINSIND": "NIFTY Infra",
    "DABUR": "NIFTY FMCG",
    "DALBHARAT": "NIFTY Infra",
    "DELHIVERY": "NIFTY Transportation",
    "DIVISLAB": "NIFTY Healthcare",
    "DIXON": "NIFTY Consumer Durables",
    "DLF": "NIFTY Realty",
    "DMART": "NIFTY Consumer Durables",
    "DRREDDY": "NIFTY Healthcare",
    "EICHERMOT": "NIFTY Auto",
    "ETERNAL": "NIFTY Services",
    "EXIDEIND": "NIFTY Auto",
    "FEDERALBNK": "NIFTY Bank",
    "FORCEMOT": "NIFTY Auto",
    "FORTIS": "NIFTY Healthcare",
    "GAIL": "NIFTY Oil & Gas",
    "GLAND": "NIFTY Pharma",
    "GLENMARK": "NIFTY Healthcare",
    "GMRAIRPORT": "NIFTY Infra",
    "GODFRYPHLP": "NIFTY FMCG",
    "GODREJCP": "NIFTY FMCG",
    "GODREJPROP": "NIFTY Realty",
    "GRASIM": "NIFTY Infra",
    "GROWW": "NIFTY Fin Service",
    "GVT&D": "NIFTY Energy",
    "HAL": "NIFTY Defence",
    "HAVELLS": "NIFTY Consumer Durables",
    "HCLTECH": "NIFTY IT",
    "HDFCAMC": "NIFTY Fin Service",
    "HDFCBANK": "NIFTY Bank",
    "HDFCLIFE": "NIFTY Fin Service",
    "HEROMOTOCO": "NIFTY Auto",
    "HINDALCO": "NIFTY Metal",
    "HINDPETRO": "NIFTY Oil & Gas",
    "HINDUNILVR": "NIFTY FMCG",
    "HINDZINC": "NIFTY Metal",
    "HYUNDAI": "NIFTY Auto",
    "ICICIAMC": "NIFTY Fin Service",
    "ICICIBANK": "NIFTY Bank",
    "ICICIGI": "NIFTY Fin Service",
    "ICICIPRULI": "NIFTY Fin Service",
    "IDEA": "NIFTY Telecom",
    "IDFCFIRSTB": "NIFTY Bank",
    "IEX": "NIFTY Fin Service",
    "INDHOTEL": "NIFTY Infra",
    "INDIANB": "NIFTY PSU Bank",
    "INDIGO": "NIFTY Infra",
    "INDUSINDBK": "NIFTY Bank",
    "INDUSTOWER": "NIFTY Infra",
    "INFY": "NIFTY IT",
    "INOXWIND": "NIFTY Energy",
    "IOC": "NIFTY Oil & Gas",
    "IPCALAB": "NIFTY Pharma",
    "IREDA": "NIFTY Fin Service",
    "IRFC": "NIFTY Fin Service",
    "ITC": "NIFTY FMCG",
    "JBCHEPHARM": "NIFTY Pharma",
    "JINDALSTEL": "NIFTY Metal",
    "JIOFIN": "NIFTY Fin Service",
    "JSWENERGY": "NIFTY Energy",
    "JSWSTEEL": "NIFTY Metal",
    "JUBLFOOD": "NIFTY Consumer Durables",
    "KALYANKJIL": "NIFTY Consumer Durables",
    "KAYNES": "NIFTY Consumer Durables",
    "KEI": "NIFTY Industrials",
    "KFINTECH": "NIFTY Fin Service",
    "KOTAKBANK": "NIFTY Bank",
    "KPITTECH": "NIFTY IT",
    "LAURUSLABS": "NIFTY Healthcare",
    "LGEINDIA": "NIFTY Consumer Durables",
    "LICHSGFIN": "NIFTY Fin Service",
    "LICI": "NIFTY Fin Service",
    "LODHA": "NIFTY Realty",
    "LT": "NIFTY Infra",
    "LTF": "NIFTY Fin Service",
    "LTM": "NIFTY IT",
    "LUPIN": "NIFTY Healthcare",
    "M&M": "NIFTY Auto",
    "MANAPPURAM": "NIFTY Fin Service",
    "MANKIND": "NIFTY Healthcare",
    "MARICO": "NIFTY FMCG",
    "MARUTI": "NIFTY Auto",
    "MAXHEALTH": "NIFTY Healthcare",
    "MAZDOCK": "NIFTY Defence",
    "MCX": "NIFTY Fin Service",
    "MFSL": "NIFTY Fin Service",
    "MOTHERSON": "NIFTY Auto",
    "MOTILALOFS": "NIFTY Fin Service",
    "MPHASIS": "NIFTY IT",
    "MUTHOOTFIN": "NIFTY Fin Service",
    "NAM-INDIA": "NIFTY Fin Service",
    "NATIONALUM": "NIFTY Metal",
    "NAUKRI": "NIFTY IT",
    "NBCC": "NIFTY Realty",
    "NESTLEIND": "NIFTY FMCG",
    "NHPC": "NIFTY Energy",
    "NMDC": "NIFTY Metal",
    "NTPC": "NIFTY Infra",
    "NUVAMA": "NIFTY Fin Service",
    "NYKAA": "NIFTY IT",
    "OBEROIRLTY": "NIFTY Realty",
    "OFSS": "NIFTY IT",
    "OIL": "NIFTY Oil & Gas",
    "ONGC": "NIFTY Oil & Gas",
    "PAGEIND": "NIFTY Consumer Durables",
    "PATANJALI": "NIFTY FMCG",
    "PAYTM": "NIFTY Fin Service",
    "PERSISTENT": "NIFTY IT",
    "PETRONET": "NIFTY Oil & Gas",
    "PFC": "NIFTY Fin Service",
    "PGEL": "NIFTY Consumer Durables",
    "PHOENIXLTD": "NIFTY Realty",
    "PIDILITIND": "NIFTY Chemicals",
    "PIIND": "NIFTY Chemicals",
    "PNB": "NIFTY PSU Bank",
    "PNBHOUSING": "NIFTY Fin Service",
    "POLICYBZR": "NIFTY Fin Service",
    "POLYCAB": "NIFTY Industrials",
    "POWERGRID": "NIFTY Infra",
    "POWERINDIA": "NIFTY Energy",
    "PREMIERENE": "NIFTY Services",
    "PRESTIGE": "NIFTY Realty",
    "RADICO": "NIFTY FMCG",
    "RBLBANK": "NIFTY Bank",
    "RECLTD": "NIFTY Fin Service",
    "RELIANCE": "NIFTY Oil & Gas",
    "RVNL": "NIFTY Realty",
    "SAIL": "NIFTY Metal",
    "SBICARD": "NIFTY Fin Service",
    "SBILIFE": "NIFTY Fin Service",
    "SBIN": "NIFTY PSU Bank",
    "SHREECEM": "NIFTY Infra",
    "SHRIRAMFIN": "NIFTY Fin Service",
    "SIEMENS": "NIFTY Energy",
    "SOLARINDS": "NIFTY Defence",
    "SONACOMS": "NIFTY Auto",
    "SRF": "NIFTY Chemicals",
    "SUNPHARMA": "NIFTY Healthcare",
    "SUPREMEIND": "NIFTY Plastics",
    "SUZLON": "NIFTY Infra",
    "SWIGGY": "NIFTY Services",
    "TATACONSUM": "NIFTY FMCG",
    "TATAELXSI": "NIFTY IT",
    "TATAPOWER": "NIFTY Infra",
    "TATASTEEL": "NIFTY Metal",
    "TCS": "NIFTY IT",
    "TECHM": "NIFTY IT",
    "TIINDIA": "NIFTY Auto",
    "TITAN": "NIFTY Consumer Durables",
    "TMPV": "NIFTY Auto",
    "TORNTPHARM": "NIFTY Healthcare",
    "TRENT": "NIFTY Consumer Durables",
    "TVSMOTOR": "NIFTY Auto",
    "ULTRACEMCO": "NIFTY Infra",
    "UNIMECH": "NIFTY Defence",
    "UNIONBANK": "NIFTY PSU Bank",
    "UNITDSPR": "NIFTY FMCG",
    "UNOMINDA": "NIFTY Auto",
    "UPL": "NIFTY Chemicals",
    "UTIAMC": "NIFTY Fin Service",
    "VBL": "NIFTY FMCG",
    "VEDL": "NIFTY Metal",
    "VMM": "NIFTY Consumer Durables",
    "VOLTAS": "NIFTY Consumer Durables",
    "WAAREEENER": "NIFTY Industrials",
    "WIPRO": "NIFTY IT",
    "WOCKPHARMA": "NIFTY Pharma",
    "YESBANK": "NIFTY Bank",
    "ZYDUSLIFE": "NIFTY Healthcare",
}

VALID_SYMBOLS = set(SECTOR_INDEX_MAP.keys())

st.set_page_config(page_title="NSE Relative Volume & Sector Tracker", layout="wide")

# Auto-refresh every 60 seconds
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
@st.cache_data(ttl=300)
def fetch_live_fno_data():
    try:
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'sector')
            .limit(1000)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]

        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector']].dropna(subset=['name', 'relative_volume_10d_calc', 'change'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector']
        
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        df = df[df['Symbol'].isin(VALID_SYMBOLS)].copy()
        
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        
        df['Sector Index'] = df['Symbol'].map(SECTOR_INDEX_MAP)
        
        return df.dropna(subset=['RelVol', 'ChangePct']).reset_index(drop=True)

    except Exception as e:
        st.error(f"Error pulling stock updates: {e}")
        return pd.DataFrame()


# ==========================================
# CALCULATIONS & PROCESSING (STOCKS)
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


def fetch_day_movers(live_df, current_time_str):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = live_df[live_df['Symbol'].isin(VALID_SYMBOLS)].copy()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")

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

    df['TradingView Chart'] = df['Symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")
    df['+1m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_1m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+3m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_3m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+5m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_5m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+15m Gain'] = df.apply(lambda r: round(r['RelVol'] - vol_15m.get(r['Symbol'], r['RelVol']), 2), axis=1)

    gainers = df.sort_values(by='ChangePct', ascending=False).head(20).copy()
    losers = df.sort_values(by='ChangePct', ascending=True).head(20).copy()

    for target_df in [gainers, losers]:
        if not target_df.empty:
            target_df['RelVol'] = target_df['RelVol'].round(2)
            target_df['ChangePct'] = target_df['ChangePct'].round(2)

    cols_order = ['Symbol', 'Sector Index', 'TradingView Chart', 'ChangePct', 'RelVol', '+1m Gain', '+3m Gain', '+5m Gain', '+15m Gain']
    col_names = ['Symbol', 'Sector Index', 'TradingView Chart', 'Price Change %', 'Relative Volume', '+1m Gain', '+3m Gain', '+5m Gain', '+15m Gain']

    if not gainers.empty:
        gainers = gainers[cols_order]
        gainers.columns = col_names

    if not losers.empty:
        losers = losers[cols_order]
        losers.columns = col_names

    return gainers.reset_index(drop=True), losers.reset_index(drop=True)


def fetch_sector_wise_data(live_df, current_time_str):
    """Calculates +1m, +3m, +5m, and +15m RelVol gains for all stocks and groups them by sector."""
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


# ==========================================
# CALCULATIONS & PROCESSING (SECTORS)
# ==========================================
def fetch_sector_comparison_data(current_time_str):
    """Calculates sector-level aggregated Relative Volume and Price Change metrics across rolling timeframes."""
    conn = sqlite3.connect(DB_NAME)
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (current_time_str,))
    latest_row = cursor.fetchone()

    if not latest_row:
        conn.close()
        return pd.DataFrame()

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

    base_df['+1m Gain'] = base_df.apply(lambda r: r['rel_vol'] - vol_1m.get(r['symbol'], r['rel_vol']), axis=1)
    base_df['+3m Gain'] = base_df.apply(lambda r: r['rel_vol'] - vol_3m.get(r['symbol'], r['rel_vol']), axis=1)
    base_df['+5m Gain'] = base_df.apply(lambda r: r['rel_vol'] - vol_5m.get(r['symbol'], r['rel_vol']), axis=1)
    base_df['+15m Gain'] = base_df.apply(lambda r: r['rel_vol'] - vol_15m.get(r['symbol'], r['rel_vol']), axis=1)

    sector_summary = base_df.groupby('sector_index').agg(
        Stock_Count=('symbol', 'count'),
        Avg_Price_Change=('change_pct', 'mean'),
        Avg_Rel_Vol=('rel_vol', 'mean'),
        Gain_1m=('+1m Gain', 'mean'),
        Gain_3m=('+3m Gain', 'mean'),
        Gain_5m=('+5m Gain', 'mean'),
        Gain_15m=('+15m Gain', 'mean')
    ).reset_index()

    sector_summary['Avg_Price_Change'] = sector_summary['Avg_Price_Change'].round(2)
    sector_summary['Avg_Rel_Vol'] = sector_summary['Avg_Rel_Vol'].round(2)
    sector_summary['Gain_1m'] = sector_summary['Gain_1m'].round(2)
    sector_summary['Gain_3m'] = sector_summary['Gain_3m'].round(2)
    sector_summary['Gain_5m'] = sector_summary['Gain_5m'].round(2)
    sector_summary['Gain_15m'] = sector_summary['Gain_15m'].round(2)

    sector_summary.columns = [
        'Sector Index', 'Stock Count', 'Avg Price Change %', 'Avg Rel Vol', 
        '+1m Sector Gain', '+3m Sector Gain', '+5m Sector Gain', '+15m Sector Gain'
    ]

    return sector_summary.sort_values(by='Avg Price Change %', ascending=False).reset_index(drop=True)


def calculate_sector_gain_by_exact_timestamps(start_ts, end_ts, label_name="Sector Rel Vol Gain"):
    """Calculates sector performance between two specific historical timestamps."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (end_ts,))
    end_row = cursor.fetchone()

    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (start_ts,))
    start_row = cursor.fetchone()

    if not end_row or not start_row or not end_row[0] or not start_row[0]:
        conn.close()
        return pd.DataFrame(), label_name

    df_end = pd.read_sql_query("SELECT symbol, rel_vol, change_pct, sector_index FROM relvol_snapshots WHERE timestamp = ?", conn, params=(end_row[0],))
    df_start = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(start_row[0],))
    conn.close()

    if df_end.empty or df_start.empty:
        return pd.DataFrame(), label_name

    merged = pd.merge(df_end, df_start, on='symbol', suffixes=('_end', '_start'))
    merged['Gain'] = merged['rel_vol_end'] - merged['rel_vol_start']

    sector_df = merged.groupby('sector_index').agg(
        Stock_Count=('symbol', 'count'),
        Avg_Price_Change=('change_pct', 'mean'),
        Avg_End_RelVol=('rel_vol_end', 'mean'),
        Avg_Sector_Gain=('Gain', 'mean')
    ).reset_index()

    sector_df['Avg_Price_Change'] = sector_df['Avg_Price_Change'].round(2)
    sector_df['Avg_End_RelVol'] = sector_df['Avg_End_RelVol'].round(2)
    sector_df['Avg_Sector_Gain'] = sector_df['Avg_Sector_Gain'].round(2)

    sector_df.columns = ['Sector Index', 'Stock Count', 'Avg Price Change %', 'Avg End Rel Vol', label_name]
    return sector_df.sort_values(by=label_name, ascending=False).reset_index(drop=True), label_name


# ==========================================
# UTILITY FUNCTIONS
# ==========================================
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
# MAIN APPLICATION WORKFLOW
# ==========================================
def main():
    init_db()
    
    now_dt = datetime.now(TIMEZONE)
    today_str = now_dt.strftime("%Y-%m-%d")
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    check_and_reset_daily(today_str)
    
    live_df = fetch_live_fno_data()
    if not live_df.empty:
        save_snapshot(live_df, now_str)

    st.title("⚡ NSE F&O Relative Volume & Sector Index Tracker")
    st.caption(f"Last updated: {now_dt.strftime('%I:%M:%S %p IST')} | Tracking {len(live_df)} F&O Symbols")

    # App Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Day Movers (Stocks)", 
        "📊 Sectoral Index Comparison", 
        "📁 Stocks Grouped by Sector", 
        "⏱️ Custom Timeframe Tracker (Stocks)"
    ])

    # Tab 1: Day Movers
    with tab1:
        st.subheader("Top Price Gainers & Losers with RelVol Metrics")
        gainers_df, losers_df = fetch_day_movers(live_df, now_str)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Top 20 Gainers")
            if not gainers_df.empty:
                st.dataframe(gainers_df.style.map(style_price_change, subset=['Price Change %']), use_container_width=True)
            else:
                st.info("No gainers data available.")
                
        with c2:
            st.markdown("### Top 20 Losers")
            if not losers_df.empty:
                st.dataframe(losers_df.style.map(style_price_change, subset=['Price Change %']), use_container_width=True)
            else:
                st.info("No losers data available.")

    # Tab 2: Sectoral Comparison
    with tab2:
        st.subheader("Sector Indices Rolling Relative Volume Performance")
        sector_summary_df = fetch_sector_comparison_data(now_str)
        
        if not sector_summary_df.empty:
            st.dataframe(
                sector_summary_df.style.map(style_price_change, subset=['Avg Price Change %']),
                use_container_width=True
            )
        else:
            st.info("Waiting for historical snapshots to populate sector comparisons...")

        st.divider()
        st.subheader("Compare Sector Indices Across Custom Time Windows")
        
        time_opts = generate_5min_time_options()
        col1, col2 = st.columns(2)
        with col1:
            start_time_lbl = st.selectbox("Sector Start Time", [t[0] for t in time_opts], index=0, key="sec_start")
        with col2:
            end_time_lbl = st.selectbox("Sector End Time", [t[0] for t in time_opts], index=len(time_opts)-1, key="sec_end")

        if st.button("Calculate Sector Gain"):
            s_time = next(t[1] for t in time_opts if t[0] == start_time_lbl)
            e_time = next(t[1] for t in time_opts if t[0] == end_time_lbl)
            
            start_ts = f"{today_str} {s_time.strftime('%H:%M:%S')}"
            end_ts = f"{today_str} {e_time.strftime('%H:%M:%S')}"
            
            custom_sec_df, _ = calculate_sector_gain_by_exact_timestamps(start_ts, end_ts)
            if not custom_sec_df.empty:
                st.dataframe(custom_sec_df.style.map(style_price_change, subset=['Avg Price Change %']), use_container_width=True)
            else:
                st.warning("Insufficient snapshot data within selected range.")

    # Tab 3: Stocks Grouped by Sector
    with tab3:
        st.subheader("Constituent Breakdown per Sector")
        sector_tables = fetch_sector_wise_data(live_df, now_str)
        
        if sector_tables:
            selected_sector = st.selectbox("Select Sector Index", list(sector_tables.keys()))
            if selected_sector in sector_tables:
                st.dataframe(
                    sector_tables[selected_sector].style.map(style_price_change, subset=['Price Change (%)']),
                    use_container_width=True
                )
        else:
            st.info("No sector data calculated yet.")

    # Tab 4: Custom Stock Timeframe Tracker
    with tab4:
        st.subheader("Stock RelVol Gain between Exact Timestamps")
        time_opts = generate_5min_time_options()
        
        sc1, sc2 = st.columns(2)
        with sc1:
            stock_start_lbl = st.selectbox("Stock Start Time", [t[0] for t in time_opts], index=0, key="stk_start")
        with sc2:
            stock_end_lbl = st.selectbox("Stock End Time", [t[0] for t in time_opts], index=len(time_opts)-1, key="stk_end")

        if st.button("Calculate Stock Gains"):
            s_time = next(t[1] for t in time_opts if t[0] == stock_start_lbl)
            e_time = next(t[1] for t in time_opts if t[0] == stock_end_lbl)
            
            start_ts = f"{today_str} {s_time.strftime('%H:%M:%S')}"
            end_ts = f"{today_str} {e_time.strftime('%H:%M:%S')}"
            
            top_stocks, label, act_start, act_end = calculate_gain_by_exact_timestamps(start_ts, end_ts)
            if not top_stocks.empty:
                st.caption(f"Comparing snapshot at **{act_start}** against **{act_end}**")
                st.dataframe(top_stocks.style.map(style_price_change, subset=['Price Change %']), use_container_width=True)
            else:
                st.warning("No stock snapshots available for selected timestamps.")


if __name__ == "__main__":
    main()
