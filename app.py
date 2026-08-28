import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
import yfinance as yf
from tradingview_screener import Query
from streamlit_autorefresh import st_autorefresh
import threading
import time as time_module

# ==========================================
# CONFIGURATION & SECTOR MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Expanded list of major NSE Sectoral and Thematic Index Tickers for TradingView
INDICES_LIST = [
    "NIFTY_BANK", "NIFTY_IT", "NIFTY_AUTO", "NIFTY_PHARMA", "NIFTY_FMCG",
    "NIFTY_METAL", "NIFTY_REALTY", "NIFTY_ENERGY", "NIFTY_INFRA", "NIFTY_MEDIA",
    "NIFTY_CONSUMPTION", "NIFTY_CPSE", "NIFTY_PSE", "NIFTY_COMMODITIES", 
    "NIFTY_MNC", "NIFTY_SERV_SECT", "NIFTY_FIN_SERVICE", "NIFTY_HEALTHCARE",
    "NIFTY_PSU_BANK", "NIFTY_OIL_AND_GAS", "NIFTY_CONSTR", "NIFTY_DEFENCE",
    "NIFTY_CONSUMER_DURABLES", "NIFTY_LOGISTICS", "NIFTY_CHEMICALS"
]

# Cleaned & Mapped Exact 200 Stock Universe
SECTOR_INDEX_MAP = {
    "360ONE": "NIFTY Fin Service", "ABB": "NIFTY Energy", "ABCAPITAL": "NIFTY Fin Service",
    "ADANIENSOL": "NIFTY Energy", "ADANIENT": "NIFTY Metal", "ADANIGREEN": "NIFTY Infra",
    "ADANIPORTS": "NIFTY Infra", "ADANIPOWER": "NIFTY Energy", "ALKEM": "NIFTY Healthcare",
    "AMBER": "NIFTY Consumer Durables", "AMBUJACEM": "NIFTY Infra", "ANGELONE": "NIFTY Fin Service",
    "APLAPOLLO": "NIFTY Metal", "APOLLOHOSP": "NIFTY Healthcare", "ASHOKLEY": "NIFTY Auto",
    "ASIANPAINT": "NIFTY Consumption", "ASTRAL": "NIFTY Infra", "ATHERENERG": "NIFTY Auto",
    "AUBANK": "NIFTY Bank", "AUROPHARMA": "NIFTY Healthcare", "AXISBANK": "NIFTY Bank",
    "BAJAJ-AUTO": "NIFTY Auto", "BAJAJFINSV": "NIFTY Fin Service", "BAJAJHLDNG": "NIFTY Fin Service",
    "BAJFINANCE": "NIFTY Fin Service", "BANDHANBNK": "NIFTY Bank", "BANKBARODA": "NIFTY PSU Bank",
    "BANKINDIA": "NIFTY PSU Bank", "BANKNIFTY": "NIFTY Bank", "BDL": "NIFTY Defence",
    "BEL": "NIFTY Defence", "BHARATFORG": "NIFTY Auto", "BHARTIARTL": "NIFTY Infra",
    "BHEL": "NIFTY Energy", "BIOCON": "NIFTY Healthcare", "BLUESTARCO": "NIFTY Consumer Durables",
    "BOSCHLTD": "NIFTY Auto", "BPCL": "NIFTY Oil & Gas", "BRITANNIA": "NIFTY FMCG",
    "BSE": "NIFTY Fin Service", "CAMS": "NIFTY Fin Service", "CANBK": "NIFTY PSU Bank",
    "CDSL": "NIFTY Fin Service", "CGPOWER": "NIFTY Infra", "CHOLAFIN": "NIFTY Fin Service",
    "CIPLA": "NIFTY Healthcare", "COALINDIA": "NIFTY Energy", "COCHINSHIP": "NIFTY Defence",
    "COFORGE": "NIFTY IT", "COLPAL": "NIFTY FMCG", "CONCOR": "NIFTY Services",
    "CROMPTON": "NIFTY Consumer Durables", "CUMMINSIND": "NIFTY Infra", "DABUR": "NIFTY FMCG",
    "DELHIVERY": "NIFTY Services", "DIVISLAB": "NIFTY Healthcare", "DIXON": "NIFTY Consumer Durables",
    "DLF": "NIFTY Realty", "DMART": "NIFTY Consumer Durables", "DRREDDY": "NIFTY Healthcare",
    "EICHERMOT": "NIFTY Auto", "ETERNAL": "NIFTY Services", "FEDERALBNK": "NIFTY Bank",
    "FORCEMOT": "NIFTY Auto", "FORTIS": "NIFTY Healthcare", "GAIL": "NIFTY Oil & Gas",
    "GLENMARK": "NIFTY Healthcare", "GODFRYPHLP": "NIFTY FMCG", "GODREJCP": "NIFTY FMCG",
    "GODREJPROP": "NIFTY Realty", "GRASIM": "NIFTY Infra", "GVT&D": "NIFTY Energy",
    "HAL": "NIFTY Defence", "HAVELLS": "NIFTY Consumer Durables", "HCLTECH": "NIFTY IT",
    "HDFCAMC": "NIFTY Fin Service", "HDFCBANK": "NIFTY Bank", "HDFCLIFE": "NIFTY Fin Service",
    "HEROMOTOCO": "NIFTY Auto", "HINDALCO": "NIFTY Metal", "HINDPETRO": "NIFTY Oil & Gas",
    "HINDUNILVR": "NIFTY FMCG", "HINDZINC": "NIFTY Metal", "HYUNDAI": "NIFTY Auto",
    "ICICIBANK": "NIFTY Bank", "ICICIGI": "NIFTY Fin Service", "ICICIPRULI": "NIFTY Fin Service",
    "IEX": "NIFTY Fin Service", "INDHOTEL": "NIFTY Services", "INDIANB": "NIFTY PSU Bank",
    "INDIGO": "NIFTY Services", "INDUSINDBK": "NIFTY Bank", "INDUSTOWER": "NIFTY Infra",
    "INFY": "NIFTY IT", "IOC": "NIFTY Oil & Gas", "IREDA": "NIFTY Fin Service",
    "ITC": "NIFTY FMCG", "JINDALSTEL": "NIFTY Metal", "JIOFIN": "NIFTY Fin Service",
    "JSWENERGY": "NIFTY Energy", "JSWSTEEL": "NIFTY Metal", "JUBLFOOD": "NIFTY Consumer Durables",
    "KALYANKJIL": "NIFTY Consumer Durables", "KAYNES": "NIFTY Consumer Durables", "KEI": "NIFTY Infra",
    "KFINTECH": "NIFTY Fin Service", "KOTAKBANK": "NIFTY Bank", "KPITTECH": "NIFTY IT",
    "LAURUSLABS": "NIFTY Healthcare", "LICHSGFIN": "NIFTY Fin Service", "LICI": "NIFTY Fin Service",
    "LODHA": "NIFTY Realty", "LT": "NIFTY Infra", "LTF": "NIFTY Fin Service",
    "LTM": "NIFTY IT", "LUPIN": "NIFTY Healthcare", "M&M": "NIFTY Auto",
    "MANAPPURAM": "NIFTY Fin Service", "MANKIND": "NIFTY Healthcare", "MARICO": "NIFTY FMCG",
    "MARUTI": "NIFTY Auto", "MAXHEALTH": "NIFTY Healthcare", "MAZDOCK": "NIFTY Defence",
    "MCX": "NIFTY Fin Service", "MFSL": "NIFTY Fin Service", "MOTHERSON": "NIFTY Auto",
    "MOTILALOFS": "NIFTY Fin Service", "MPHASIS": "NIFTY IT", "MUTHOOTFIN": "NIFTY Fin Service",
    "NAM-INDIA": "NIFTY Fin Service", "NATIONALUM": "NIFTY Metal", "NAUKRI": "NIFTY IT",
    "NESTLEIND": "NIFTY FMCG", "NIFTY": "NIFTY Index", "NTPC": "NIFTY Infra",
    "NYKAA": "NIFTY IT", "OBEROIRLTY": "NIFTY Realty", "OFSS": "NIFTY IT",
    "OIL": "NIFTY Oil & Gas", "ONGC": "NIFTY Oil & Gas", "PAGEIND": "NIFTY Consumer Durables",
    "PATANJALI": "NIFTY FMCG", "PAYTM": "NIFTY Fin Service", "PERSISTENT": "NIFTY IT",
    "PETRONET": "NIFTY Oil & Gas", "PFC": "NIFTY Fin Service", "PGEL": "NIFTY Consumer Durables",
    "PHOENIXLTD": "NIFTY Realty", "PIDILITIND": "NIFTY Chemicals", "PIIND": "NIFTY Chemicals",
    "PNB": "NIFTY PSU Bank", "PNBHOUSING": "NIFTY Fin Service", "POLICYBZR": "NIFTY Fin Service",
    "POLYCAB": "NIFTY Infra", "POWERGRID": "NIFTY Infra", "POWERINDIA": "NIFTY Energy",
    "PREMIERENE": "NIFTY Energy", "PRESTIGE": "NIFTY Realty", "RADICO": "NIFTY FMCG",
    "RBLBANK": "NIFTY Bank", "RECLTD": "NIFTY Fin Service", "RELIANCE": "NIFTY Oil & Gas",
    "RVNL": "NIFTY Infra", "SAIL": "NIFTY Metal", "SBICARD": "NIFTY Fin Service",
    "SBILIFE": "NIFTY Fin Service", "SBIN": "NIFTY PSU Bank", "SHREECEM": "NIFTY Infra",
    "SHRIRAMFIN": "NIFTY Fin Service", "SIEMENS": "NIFTY Energy", "SOLARINDS": "NIFTY Defence",
    "SONACOMS": "NIFTY Auto", "SRF": "NIFTY Chemicals", "SUNPHARMA": "NIFTY Healthcare",
    "SUPREMEIND": "NIFTY Infra", "SWIGGY": "NIFTY Services", "TATACONSUM": "NIFTY FMCG",
    "TATAELXSI": "NIFTY IT", "TATAPOWER": "NIFTY Infra", "TATASTEEL": "NIFTY Metal",
    "TCS": "NIFTY IT", "TECHM": "NIFTY IT", "TIINDIA": "NIFTY Auto",
    "TITAN": "NIFTY Consumer Durables", "TMPV": "NIFTY Auto", "TORNTPHARM": "NIFTY Healthcare",
    "TRENT": "NIFTY Consumer Durables", "TVSMOTOR": "NIFTY Auto", "ULTRACEMCO": "NIFTY Infra",
    "UNIONBANK": "NIFTY PSU Bank", "UNITDSPR": "NIFTY FMCG", "UNOMINDA": "NIFTY Auto",
    "UPL": "NIFTY Chemicals", "VBL": "NIFTY FMCG", "VEDL": "NIFTY Metal",
    "VMM": "NIFTY Consumer Durables", "VOLTAS": "NIFTY Consumer Durables", "WAAREEENER": "NIFTY Energy",
    "WIPRO": "NIFTY IT", "ZYDUSLIFE": "NIFTY Healthcare"
}

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

st_autorefresh(interval=30000, key="datarefresh")

# ==========================================
# THREAD-SAFE DATABASE HELPER FUNCTIONS
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relvol_snapshots (
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                rel_vol REAL NOT NULL,
                change_pct REAL,
                sector_index TEXT,
                pdh_status TEXT,
                PRIMARY KEY (timestamp, symbol)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("PRAGMA table_info(relvol_snapshots);")
        columns = [column[1] for column in cursor.fetchall()]
        if "pdh_status" not in columns:
            cursor.execute("ALTER TABLE relvol_snapshots ADD COLUMN pdh_status TEXT;")
        conn.commit()

def check_and_reset_daily(today_date_str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_config WHERE key = 'last_reset_date'")
        row = cursor.fetchone()
        
        if not row or row[0] != today_date_str:
            cursor.execute("DELETE FROM relvol_snapshots")
            cursor.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('last_reset_date', ?)", (today_date_str,))
            conn.commit()

def save_snapshot(df, now_str):
    if df.empty:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        data = [
            (now_str, row['Symbol'], float(row['RelVol']), float(row['ChangePct']), str(row['Sector Index']), str(row['PDH_Status']))
            for _, row in df.iterrows()
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO relvol_snapshots (timestamp, symbol, rel_vol, change_pct, sector_index, pdh_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()

# ==========================================
# YFINANCE PRE-FETCHING (CORRECTED PDH/PDL)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_pdh_pdl_dict(symbol_tuple):
    symbol_list = list(symbol_tuple)
    pdh_pdl_map = {}
    if not symbol_list:
        return pdh_pdl_map

    yf_symbols = [f"{s}.NS" for s in symbol_list]
    
    try:
        data = yf.download(yf_symbols, period="5d", interval="1d", progress=False)
        
        if data.empty:
            return pdh_pdl_map

        for sym in symbol_list:
            ticker_yf = f"{sym}.NS"
            try:
                if len(symbol_list) == 1:
                    df_sym = data[['High', 'Low']].dropna()
                else:
                    if ticker_yf in data['High'].columns:
                        high_series = data['High'][ticker_yf]
                        low_series = data['Low'][ticker_yf]
                        df_sym = pd.DataFrame({'High': high_series, 'Low': low_series}).dropna()
                    else:
                        continue

                if len(df_sym) >= 2:
                    prev_day = df_sym.iloc[-2]
                    pdh = float(prev_day['High'])
                    pdl = float(prev_day['Low'])
                    
                    if not (pd.isna(pdh) or pd.isna(pdl)):
                        pdh_pdl_map[sym] = {
                            'PDH': pdh,
                            'PDL': pdl
                        }
            except Exception:
                continue

    except Exception as e:
        print(f"Error fetching PDH/PDL via yfinance: {e}")

    return pdh_pdl_map

# ==========================================
# DYNAMIC SCANNER FETCHING
# ==========================================
def fetch_live_fno_data(stock_universe_mode="Nifty 500 Stocks"):
    try:
        limit = 500
        
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'sector', 'close', 'high', 'low')
            .limit(limit)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]

        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector', 'close', 'high', 'low']].dropna(subset=['name', 'relative_volume_10d_calc'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector', 'Close', 'High', 'Low']
        
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        
        # Apply filtering according to selected stock universe
        if stock_universe_mode == "Custom 200 List":
            target_universe = set(SECTOR_INDEX_MAP.keys())
            df = df[df['Symbol'].isin(target_universe)].copy()

        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')

        symbols_tuple = tuple(df['Symbol'].tolist())
        pdh_pdl_map = fetch_pdh_pdl_dict(symbols_tuple)

        df['PDH'] = df['Symbol'].apply(lambda s: pdh_pdl_map.get(s, {}).get('PDH', None))
        df['PDL'] = df['Symbol'].apply(lambda s: pdh_pdl_map.get(s, {}).get('PDL', None))

        def check_pdh_pdl(row):
            if pd.notnull(row['High']) and pd.notnull(row['PDH']) and row['High'] > row['PDH']:
                return "PDH Cross 🟢"
            elif pd.notnull(row['Low']) and pd.notnull(row['PDL']) and row['Low'] < row['PDL']:
                return "PDL Cross 🔴"
            else:
                return "Inside Range ➖"

        df['PDH_Status'] = df.apply(check_pdh_pdl, axis=1)
        df['Sector Index'] = df['Symbol'].map(SECTOR_INDEX_MAP).fillna(df['TV Sector'].fillna("Other Sector"))
        
        return df.dropna(subset=['RelVol', 'ChangePct']).reset_index(drop=True)

    except Exception as e:
        print(f"Error pulling stock updates: {e}")
        return pd.DataFrame()

def fetch_live_indices_data():
    try:
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'close')
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]

        if df is None or df.empty:
            return pd.DataFrame()

        df = df[['name', 'relative_volume_10d_calc', 'change']].dropna()
        df.columns = ['Symbol', 'RelVol', 'ChangePct']

        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        df = df[df['Symbol'].isin(INDICES_LIST)].copy()

        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        df['Sector Index'] = "Index"
        df['PDH_Status'] = "N/A"

        return df.dropna().reset_index(drop=True)
    except Exception as e:
        print(f"Error pulling indices data: {e}")
        return pd.DataFrame()

# ==========================================
# BACKGROUND AUTOMATIC SNAPSHOT SCHEDULER
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
                    
                    df = fetch_live_fno_data("Nifty 500 Stocks")
                    indices_df = fetch_live_indices_data()
                    combined_df = pd.concat([df, indices_df], ignore_index=True)

                    if not combined_df.empty:
                        save_snapshot(combined_df, now_str)
        except Exception as e:
            print(f"Background Snapshot Exception: {e}")
            
        time_module.sleep(30)

init_db()

if "bg_thread_started" not in st.session_state:
    st.session_state["bg_thread_started"] = True
    bg_thread = threading.Thread(target=auto_snapshot_loop, daemon=True)
    bg_thread.start()

# ==========================================
# CALCULATIONS & PROCESSING
# ==========================================
def calculate_gain_by_exact_timestamps(start_ts, end_ts, label_name="Gain"):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (end_ts,))
        end_row = cursor.fetchone()
        
        cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (start_ts,))
        start_row = cursor.fetchone()

        if not end_row or not start_row or not end_row[0] or not start_row[0]:
            return pd.DataFrame(), label_name, None, None

        actual_start_ts = start_row[0]
        actual_end_ts = end_row[0]

        df_end = pd.read_sql_query(
            "SELECT symbol, rel_vol, change_pct, sector_index, COALESCE(pdh_status, 'Inside Range ➖') as pdh_status FROM relvol_snapshots WHERE timestamp = ?", 
            conn, 
            params=(actual_end_ts,)
        )
        df_start = pd.read_sql_query(
            "SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", 
            conn, 
            params=(actual_start_ts,)
        )

    if df_end.empty or df_start.empty:
        return pd.DataFrame(), label_name, actual_start_ts, actual_end_ts

    merged = pd.merge(df_end, df_start, on='symbol', suffixes=('_end', '_start'))
    merged['Gain'] = merged['rel_vol_end'] - merged['rel_vol_start']

    top = merged.sort_values(by='Gain', ascending=False).head(20).copy()
    top['TradingView Chart'] = top['symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    top = top[['symbol', 'pdh_status', 'sector_index', 'TradingView Chart', 'change_pct', 'rel_vol_end', 'Gain']].copy()
    top['rel_vol_end'] = top['rel_vol_end'].round(2)
    top['Gain'] = top['Gain'].round(2)
    top['change_pct'] = top['change_pct'].round(2)

    top.columns = ['Symbol', 'PDH/PDL Status', 'Sector Index', 'TradingView Chart', 'Price Change %', 'End Rel Vol', label_name]
    return top.reset_index(drop=True), label_name, actual_start_ts, actual_end_ts

def calculate_gain_relative(minutes, current_time_str):
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    start_str = (curr_dt - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    df, label, _, _ = calculate_gain_by_exact_timestamps(start_str, current_time_str, f'+{minutes}m Gain')
    return df, label

def fetch_day_movers_with_multi_timeframes(live_df, current_time_str):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")

    def get_past_relvol(mins):
        past_str = (curr_dt - timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
        with get_db_connection() as conn:
            cursor = conn.cursor()
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
        'Symbol', 'PDH_Status', 'Sector Index', 'TradingView Chart', 'ChangePct',
        'RelVol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain'
    ]
    col_names = [
        'Stock Symbol', 'PDH/PDL Status', 'Sector Index', 'TradingView Chart', 'Price Change (%)',
        'End Rel Vol', '+1m Gain', '+3m Gain', '+5m Gain', '+10m Gain', '+15m Gain'
    ]

    if not gainers.empty:
        gainers = gainers[cols_order]
        gainers.columns = col_names

    if not losers.empty:
        losers = losers[cols_order]
        losers.columns = col_names

    df_renamed = df[cols_order].copy()
    df_renamed.columns = col_names

    return gainers.reset_index(drop=True), losers.reset_index(drop=True), df_renamed.reset_index(drop=True)

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

LINK_COLUMN_CONFIG = {
    "TradingView Chart": st.column_config.LinkColumn(
        "TradingView Chart",
        display_text="Open Chart 📈"
    )
}

# ==========================================
# DASHBOARD UI
# ==========================================
now_dt = datetime.now(TIMEZONE)
now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now_dt.strftime("%Y-%m-%d")

st.sidebar.header("📌 Stock Universe Selection")
stock_universe_mode = st.sidebar.radio(
    "Choose Stock Universe:",
    options=["Custom 200 List", "Nifty 500 Stocks"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Custom Time Range")

time_options = generate_5min_time_options()
time_labels = [opt[0] for opt in time_options]

selected_start_label = st.sidebar.selectbox("Select Start Time:", options=time_labels, index=0)
start_idx = time_labels.index(selected_start_label)
default_end_idx = min(start_idx + 1, len(time_labels) - 1)
selected_end_label = st.sidebar.selectbox("Select End Time:", options=time_labels, index=default_end_idx)

custom_start_time = next(opt[1] for opt in time_options if opt[0] == selected_start_label)
custom_end_time = next(opt[1] for opt in time_options if opt[0] == selected_end_label)

live_df = fetch_live_fno_data(stock_universe_mode)
indices_df = fetch_live_indices_data()

st.title("⚡ NSE Relative Volume & Price Movers")
st.caption(f"Active Universe: **{stock_universe_mode} ({len(live_df)} Loaded)** | PDH/PDL Scanner: 🟢 **Active** | Refreshed: {now_str} IST")

tab1, tab3, tab5, tab10, tab15, tab_custom, tab_day, tab_nifty500, tab_sectors, tab_indices = st.tabs([
    "1 Min", "3 Min", "5 Min", "10 Min", "15 Min", "🎯 Custom Range", "🔥 Top Gainers/Losers", "🌐 Nifty 500", "📂 Sectors", "📊 Sector & Thematic Indices"
])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 20 Volume Gainers - Last {mins} Minute(s)")
        df_gain, gain_col_name = calculate_gain_relative(mins, now_str)
        if not df_gain.empty:
            styled_df = df_gain.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(styled_df, column_config=LINK_COLUMN_CONFIG, use_container_width=True)
        else:
            st.info("Accumulating minute-by-minute background snapshots... Please wait.")

with tab_custom:
    st.subheader(f"Top 20 RelVol Gainers: {selected_start_label} ➔ {selected_end_label}")
    if custom_start_time < custom_end_time:
        start_ts_str = f"{today_date_str} {custom_start_time.strftime('%H:%M:%S')}"
        end_ts_str = f"{today_date_str} {custom_end_time.strftime('%H:%M:%S')}"
        df_custom, gain_col_name, act_start, act_end = calculate_gain_by_exact_timestamps(start_ts_str, end_ts_str, label_name="Custom Window Gain")
        if not df_custom.empty:
            styled_custom = df_custom.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(styled_custom, column_config=LINK_COLUMN_CONFIG, use_container_width=True)

with tab_day:
    st.subheader("🔥 Top 20 Day Gainers & Losers with Multi-Timeframe Volume Momentum")
    gainers_df, losers_df, full_df = fetch_day_movers_with_multi_timeframes(live_df, now_str)
    if not gainers_df.empty:
        st.markdown("### 🟢 Top 20 Day Gainers (% Increase)")
        st.dataframe(gainers_df.style.map(style_price_change, subset=['Price Change (%)']).format({'Price Change (%)': '{:+.2f}%'}), column_config=LINK_COLUMN_CONFIG, use_container_width=True)
    if not losers_df.empty:
        st.markdown("### 🔴 Top 20 Day Losers (% Drop)")
        st.dataframe(losers_df.style.map(style_price_change, subset=['Price Change (%)']).format({'Price Change (%)': '{:+.2f}%'}), column_config=LINK_COLUMN_CONFIG, use_container_width=True)

# ==========================================
# TAB: NIFTY 500 STOCKS
# ==========================================
with tab_nifty500:
    st.subheader("🌐 Nifty 500 Broad Universe Relative Volume Scanner")
    nifty500_df = fetch_live_fno_data("Nifty 500 Stocks")
    
    if not nifty500_df.empty:
        _, _, nifty500_tf_df = fetch_day_movers_with_multi_timeframes(nifty500_df, now_str)
        nifty500_tf_df = nifty500_tf_df.sort_values(by='End Rel Vol', ascending=False).reset_index(drop=True)
        
        styled_nifty500 = nifty500_tf_df.style.map(
            style_price_change, subset=['Price Change (%)']
        ).format({'Price Change (%)': '{:+.2f}%'})

        st.dataframe(
            styled_nifty500, 
            column_config=LINK_COLUMN_CONFIG, 
            use_container_width=True
        )
    else:
        st.info("Fetching Nifty 500 stock universe relative volume data...")

# ==========================================
# TAB: SECTOR WISE ANALYSIS
# ==========================================
with tab_sectors:
    st.subheader("📂 Sector-Wise Relative Volume & Momentum")
    _, _, full_df = fetch_day_movers_with_multi_timeframes(live_df, now_str)

    if not full_df.empty:
        st.markdown("### 📊 Sector Volume & Price Overview")
        sector_summary = full_df.groupby('Sector Index').agg(
            Stock_Count=('Stock Symbol', 'count'),
            Avg_RelVol=('End Rel Vol', 'mean'),
            Avg_Price_Change=('Price Change (%)', 'mean')
        ).reset_index()

        sector_summary['Avg_RelVol'] = sector_summary['Avg_RelVol'].round(2)
        sector_summary['Avg_Price_Change'] = sector_summary['Avg_Price_Change'].round(2)
        sector_summary = sector_summary.sort_values(by='Avg_RelVol', ascending=False)
        
        sector_summary.columns = ['Sector Index', 'Total Stocks', 'Average Rel Vol', 'Average Price Change (%)']
        
        styled_summary = sector_summary.style.map(
            style_price_change, subset=['Average Price Change (%)']
        ).format({'Average Price Change (%)': '{:+.2f}%'})
        
        st.dataframe(styled_summary, use_container_width=True)

        st.markdown("---")

        st.markdown("### 🎯 Filter Stocks by Sector")
        all_sectors = sorted(full_df['Sector Index'].unique().tolist())
        selected_sector = st.selectbox("Select Sector:", options=all_sectors)

        sector_stocks = full_df[full_df['Sector Index'] == selected_sector].sort_values(
            by='End Rel Vol', ascending=False
        ).reset_index(drop=True)

        styled_sector_stocks = sector_stocks.style.map(
            style_price_change, subset=['Price Change (%)']
        ).format({'Price Change (%)': '{:+.2f}%'})

        st.dataframe(
            styled_sector_stocks, 
            column_config=LINK_COLUMN_CONFIG, 
            use_container_width=True
        )
    else:
        st.info("Loading sector relative volume data...")

# ==========================================
# TAB: SECTOR & THEMATIC INDICES
# ==========================================
with tab_indices:
    st.subheader("📊 Sectoral & Thematic Indices Relative Volume Tracking")
    
    if not indices_df.empty:
        _, _, indices_tf_df = fetch_day_movers_with_multi_timeframes(indices_df, now_str)
        
        indices_tf_df = indices_tf_df.drop(columns=['PDH/PDL Status', 'Sector Index'], errors='ignore')
        indices_tf_df = indices_tf_df.sort_values(by='End Rel Vol', ascending=False).reset_index(drop=True)
        
        styled_indices = indices_tf_df.style.map(
            style_price_change, subset=['Price Change (%)']
        ).format({'Price Change (%)': '{:+.2f}%'})

        st.dataframe(
            styled_indices, 
            column_config=LINK_COLUMN_CONFIG, 
            use_container_width=True
        )
    else:
        st.info("Fetching Sectoral and Thematic Indices relative volume data...")
