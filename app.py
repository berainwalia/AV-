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

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

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
# MAIN STREAMLIT APPLICATION EXECUTION
# ==========================================
init_db()

now_kolkata = datetime.now(TIMEZONE)
today_str = now_kolkata.strftime("%Y-%m-%d")
now_str = now_kolkata.strftime("%Y-%m-%d %H:%M:%S")

check_and_reset_daily(today_str)

st.title("📊 NSE Relative Volume & F&O Tracker")
st.caption(f"Last Refreshed (IST): **{now_str}**")

# Fetch and store live snapshot
live_df = fetch_live_fno_data()
if not live_df.empty:
    save_snapshot(live_df, now_str)
else:
    st.warning("Unable to retrieve live market data or market is currently offline.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Day Movers", 
    "⏱️ RelVol Lookback Gainers", 
    "🎯 Custom Time Comparison", 
    "🏢 Sector Breakdown"
])

link_config = {
    "TradingView Chart": st.column_config.LinkColumn("Chart", display_text="Open Chart"),
    "Chart Link": st.column_config.LinkColumn("Chart", display_text="Open Chart")
}

# --- TAB 1: DAY MOVERS ---
with tab1:
    st.subheader("Top Price Gainers & Losers with RelVol Momentum")
    gainers_df, losers_df = fetch_day_movers(live_df, now_str)
    
    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("### 🟢 Top 20 Gainers")
        if not gainers_df.empty:
            st.dataframe(
                gainers_df.style.map(style_price_change, subset=['Price Change %']),
                column_config=link_config,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No gainer data available yet.")
            
    with col_l:
        st.markdown("### 🔴 Top 20 Losers")
        if not losers_df.empty:
            st.dataframe(
                losers_df.style.map(style_price_change, subset=['Price Change %']),
                column_config=link_config,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No loser data available yet.")

# --- TAB 2: RELATIVE LOOKBACK ---
with tab2:
    st.subheader("Volume Surge Lookback Analysis")
    selected_tf = st.selectbox("Select Lookback Minutes", [1, 3, 5, 15], index=2, format_func=lambda x: f"Last {x} Minutes")
    
    rel_gain_df, _ = calculate_gain_relative(selected_tf, now_str)
    if not rel_gain_df.empty:
        st.dataframe(
            rel_gain_df.style.map(style_price_change, subset=['Price Change %']),
            column_config=link_config,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Gathering historical snapshots. Please allow a few minutes for interval calculation.")

# --- TAB 3: CUSTOM TIME COMPARISON ---
with tab3:
    st.subheader("Compare Volume Spike Between Selected Times")
    time_options = generate_5min_time_options()
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_label, start_time_val = st.selectbox("Start Time", time_options, index=0, key="start_t")
    with col_t2:
        end_label, end_time_val = st.selectbox("End Time", time_options, index=len(time_options)-1, key="end_t")
        
    start_ts_str = f"{today_str} {start_time_val.strftime('%H:%M:%S')}"
    end_ts_str = f"{today_str} {end_time_val.strftime('%H:%M:%S')}"
    
    if st.button("Calculate RelVol Gain", type="primary"):
        custom_df, label, act_start, act_end = calculate_gain_by_exact_timestamps(start_ts_str, end_ts_str, "Volume Gain")
        if not custom_df.empty:
            st.caption(f"Comparing nearest recorded timestamps: **{act_start}** ➔ **{act_end}**")
            st.dataframe(
                custom_df.style.map(style_price_change, subset=['Price Change %']),
                column_config=link_config,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No records found in database for the chosen timeframe.")

# --- TAB 4: SECTOR VIEW ---
with tab4:
    st.subheader("Sector Breakdown")
    sector_map = fetch_sector_wise_data(live_df, now_str)
    if sector_map:
        selected_sector = st.selectbox("Select Sector Index", list(sector_map.keys()))
        if selected_sector:
            st.dataframe(
                sector_map[selected_sector].style.map(style_price_change, subset=['Price Change (%)']),
                column_config=link_config,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No sector data calculated yet.")
