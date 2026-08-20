import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query, Column
from streamlit_autorefresh import st_autorefresh
import threading
import time as time_module
import yfinance as yf

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

st.set_page_config(page_title="NSE Relative Volume & PDH/PDL Tracker", layout="wide")

# UI Auto-refresh every 30 seconds
st_autorefresh(interval=30000, key="datarefresh")

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
# ACCURATE YFINANCE PDH / PDL FETCHING
# ==========================================

def fetch_pdh_pdl_dict(symbols_list):
    """Fetches Previous Day High & Low accurately via yfinance."""
    pdh_pdl_map = {}
    formatted_symbols = [f"{s}.NS" for s in symbols_list]
    
    try:
        data = yf.download(formatted_symbols, period="5d", interval="1d", progress=False)
        if not data.empty and 'High' in data and 'Low' in data:
            highs = data['High']
            lows = data['Low']
            
            for symbol in symbols_list:
                ticker_sym = f"{symbol}.NS"
                try:
                    if len(symbols_list) == 1:
                        s_highs = highs.dropna()
                        s_lows = lows.dropna()
                    else:
                        s_highs = highs[ticker_sym].dropna()
                        s_lows = lows[ticker_sym].dropna()
                    
                    if len(s_highs) >= 2:
                        pdh = round(float(s_highs.iloc[-2]), 2)
                        pdl = round(float(s_lows.iloc[-2]), 2)
                        pdh_pdl_map[symbol] = {'PDH': pdh, 'PDL': pdl}
                except Exception:
                    continue
    except Exception as e:
        print(f"Error fetching yfinance PDH/PDL: {e}")
        
    return pdh_pdl_map

@st.cache_data(ttl=86400)
def get_cached_pdh_pdl(today_str, symbols_tuple):
    return fetch_pdh_pdl_dict(list(symbols_tuple))

# ==========================================
# DYNAMIC SCANNER FETCHING (WITH REAL-TIME PDH/PDL)
# ==========================================

def fetch_live_fno_data(stock_universe_mode="Custom List"):
    try:
        limit = 200 if stock_universe_mode == "Custom List" else 500
        
        # 1. Fetch live intraday prices from TradingView
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
        
        if stock_universe_mode == "Custom List":
            df = df[df['Symbol'].isin(VALID_SYMBOLS)].copy()
            
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        
        # 2. Merge with Cached Previous Day High / Low
        today_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
        all_symbols = tuple(df['Symbol'].tolist())
        pdh_pdl_map = get_cached_pdh_pdl(today_str, all_symbols)
        
        df['PDH'] = df['Symbol'].apply(lambda s: pdh_pdl_map.get(s, {}).get('PDH', None))
        df['PDL'] = df['Symbol'].apply(lambda s: pdh_pdl_map.get(s, {}).get('PDL', None))
        
        # 3. Dynamic Real-Time Breakout Check
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
                    
                    df = fetch_live_fno_data("All Stocks")
                    if not df.empty:
                        save_snapshot(df, now_str)
        except Exception as e:
            print(f"Background Snapshot Exception: {e}")
        time_module.sleep(30)

init_db()

if "bg_thread_started" not in st.session_state:
    st.session_state["bg_thread_started"] = True
    bg_thread = threading.Thread(target=auto_snapshot_loop, daemon=True)
    bg_thread.start()

# ==========================================
# STREAMLIT UI RENDER
# ==========================================

st.title("📈 NSE Real-Time Relative Volume & PDH/PDL Tracker")

universe_option = st.radio(
    "Select Stock Universe:",
    options=["Custom List", "All Stocks"],
    horizontal=True
)

now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
live_df = fetch_live_fno_data(universe_option)

st.write(f"**Last Updated:** {now_str}")

if not live_df.empty:
    display_cols = ['Symbol', 'Sector Index', 'Close', 'High', 'Low', 'PDH', 'PDL', 'PDH_Status', 'RelVol', 'ChangePct']
    st.dataframe(live_df[display_cols], use_container_width=True)
else:
    st.warning("Fetching live stock data... Please wait.")
