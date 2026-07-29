import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from tradingview_screener import Query
from streamlit_autorefresh import st_autorefresh

# ==========================================
# CONFIGURATION & SECTOR INDEX MAPPINGS
# ==========================================
DB_NAME = "relvol_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Mapping of stock symbols to their respective NSE Sectoral Indices
SECTOR_INDEX_MAP = {
    # NIFTY BANK / FINANCIAL SERVICES
    "HDFCBANK": "NIFTY Bank", "ICICIBANK": "NIFTY Bank", "SBIN": "NIFTY Bank",
    "AXISBANK": "NIFTY Bank", "KOTAKBANK": "NIFTY Bank", "INDUSINDBK": "NIFTY Bank",
    "BANKBARODA": "NIFTY Bank", "PNB": "NIFTY Bank", "CANBK": "NIFTY Bank",
    "AUBANK": "NIFTY Bank", "FEDERALBNK": "NIFTY Bank", "IDFCFIRSTB": "NIFTY Bank",
    "BANDHANBNK": "NIFTY Bank", "RBLBANK": "NIFTY Bank", "BAJFINANCE": "NIFTY Fin Service",
    "BAJAJFINSV": "NIFTY Fin Service", "CHOLAFIN": "NIFTY Fin Service", "PFC": "NIFTY Fin Service",
    "RECLTD": "NIFTY Fin Service", "SHRIRAMFIN": "NIFTY Fin Service", "MUTHOOTFIN": "NIFTY Fin Service",
    "SBILIFE": "NIFTY Fin Service", "HDFCLIFE": "NIFTY Fin Service", "ICICIPRULI": "NIFTY Fin Service",
    "ICICIGI": "NIFTY Fin Service", "MCX": "NIFTY Fin Service",

    # NIFTY IT
    "TCS": "NIFTY IT", "INFY": "NIFTY IT", "HCLTECH": "NIFTY IT",
    "WIPRO": "NIFTY IT", "TECHM": "NIFTY IT", "LTIM": "NIFTY IT",
    "PERSISTENT": "NIFTY IT", "COFORGE": "NIFTY IT", "MPHASIS": "NIFTY IT",
    "LTTS": "NIFTY IT", "BSOFT": "NIFTY IT", "OFSS": "NIFTY IT",

    # NIFTY AUTO
    "TATAMOTORS": "NIFTY Auto", "M&M": "NIFTY Auto", "MARUTI": "NIFTY Auto",
    "BAJAJ-AUTO": "NIFTY Auto", "EICHERMOT": "NIFTY Auto", "HEROMOTOCO": "NIFTY Auto",
    "TVSMOTOR": "NIFTY Auto", "ASHOKLEY": "NIFTY Auto", "BHARATFORG": "NIFTY Auto",
    "BALKRISIND": "NIFTY Auto", "MRF": "NIFTY Auto", "MOTHERSON": "NIFTY Auto",
    "APOLLOTYRE": "NIFTY Auto", "ESCORTS": "NIFTY Auto",

    # NIFTY PHARMA / HEALTHCARE
    "SUNPHARMA": "NIFTY Pharma", "CIPLA": "NIFTY Pharma", "DRREDDY": "NIFTY Pharma",
    "DIVISLAB": "NIFTY Pharma", "ZYDUSLIFE": "NIFTY Pharma", "TORNTPHARM": "NIFTY Pharma",
    "LUPIN": "NIFTY Pharma", "AUROPHARMA": "NIFTY Pharma", "ALKEM": "NIFTY Pharma",
    "GLENMARK": "NIFTY Pharma", "BIOCON": "NIFTY Pharma", "IPCALAB": "NIFTY Pharma",
    "APOLLOHOSP": "NIFTY Healthcare", "LALPATHLAB": "NIFTY Healthcare", "METROPOLIS": "NIFTY Healthcare",
    "SYNGENE": "NIFTY Healthcare", "GRANULES": "NIFTY Pharma", "ABBOTINDIA": "NIFTY Pharma",

    # NIFTY METAL
    "TATASTEEL": "NIFTY Metal", "JSWSTEEL": "NIFTY Metal", "HINDALCO": "NIFTY Metal",
    "JINDALSTEL": "NIFTY Metal", "VEDL": "NIFTY Metal", "VDL": "NIFTY Metal",
    "NMDC": "NIFTY Metal", "SAIL": "NIFTY Metal", "NATIONALUM": "NIFTY Metal",
    "HINDCOPPER": "NIFTY Metal",

    # NIFTY FMCG / CONSUMPTION
    "ITC": "NIFTY FMCG", "HINDUNILVR": "NIFTY FMCG", "BRITANNIA": "NIFTY FMCG",
    "NESTLEIND": "NIFTY FMCG", "DABUR": "NIFTY FMCG", "GODREJCP": "NIFTY FMCG",
    "MARICO": "NIFTY FMCG", "COLPAL": "NIFTY FMCG", "TATACONSUM": "NIFTY FMCG",
    "MCDOWELL-N": "NIFTY FMCG", "UBL": "NIFTY FMCG", "BALRAMCHIN": "NIFTY FMCG",

    # NIFTY ENERGY / OIL & GAS / POWER
    "RELIANCE": "NIFTY Oil & Gas", "ONGC": "NIFTY Oil & Gas", "IOC": "NIFTY Oil & Gas",
    "BPCL": "NIFTY Oil & Gas", "HPCL": "NIFTY Oil & Gas", "HINDPETRO": "NIFTY Oil & Gas",
    "GAIL": "NIFTY Oil & Gas", "PETRONET": "NIFTY Oil & Gas", "IGL": "NIFTY Oil & Gas",
    "MGL": "NIFTY Oil & Gas", "GUJGASLTD": "NIFTY Oil & Gas", "NTPC": "NIFTY Power",
    "POWERGRID": "NIFTY Power", "TATAPOWER": "NIFTY Power", "COALINDIA": "NIFTY Energy",

    # NIFTY REALTY & INFRASTRUCTURE
    "DLF": "NIFTY Realty", "GODREJPROP": "NIFTY Realty", "OBEROIRLTY": "NIFTY Realty",
    "LT": "NIFTY Infra", "HAL": "NIFTY PSE/Defence", "BEL": "NIFTY PSE/Defence",
    "BHEL": "NIFTY Infra", "SIEMENS": "NIFTY Infra", "ABB": "NIFTY Infra",
    "CUMMINSIND": "NIFTY Infra", "CONCOR": "NIFTY Infra", "GMRINFRA": "NIFTY Infra",
    "GMRAIRPORT": "NIFTY Infra", "IRCTC": "NIFTY Infra", "IRFC": "NIFTY Infra",

    # NIFTY CONSUMER DURABLES / RETAIL
    "TITAN": "NIFTY Consumer Durables", "HAVEL": "NIFTY Consumer Durables", "HAVELLS": "NIFTY Consumer Durables",
    "VOLTAS": "NIFTY Consumer Durables", "CROMPTON": "NIFTY Consumer Durables", "DIXON": "NIFTY Consumer Durables",
    "POLYCAB": "NIFTY Consumer Durables", "ASTRAL": "NIFTY Consumer Durables", "ASIANPAINT": "NIFTY Consumer Durables",
    "BERGEPAINT": "NIFTY Consumer Durables", "TRENT": "NIFTY Retail", "ABFRL": "NIFTY Retail",
    "JUBLFOOD": "NIFTY Retail", "PVRINOX": "NIFTY Media", "ZEEL": "NIFTY Media", "SUNTV": "NIFTY Media"
}

# Active F&O stock set
FNO_STOCKS = set(SECTOR_INDEX_MAP.keys())

st.set_page_config(page_title="TradingView RelVol Dashboard", layout="wide")

# Auto-refresh dashboard every 60 seconds
st_autorefresh(interval=60000, key="datarefresh")

# ==========================================
# DATABASE FUNCTIONS WITH AUTO-MIGRATION
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
    
    # Auto-migration check: ensure 'sector_index' column exists
    cursor.execute("PRAGMA table_info(relvol_snapshots)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'sector_index' not in columns:
        cursor.execute("ALTER TABLE relvol_snapshots ADD COLUMN sector_index TEXT")
        
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
    cursor.executemany("INSERT OR REPLACE INTO relvol_snapshots VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def fetch_live_data():
    try:
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change')
            .limit(250)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]
        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change']].dropna()
        df.columns = ['Symbol', 'RelVol', 'ChangePct']
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        
        # Map each stock symbol to its Sector Index
        df['Sector Index'] = df['Symbol'].apply(lambda s: SECTOR_INDEX_MAP.get(s.upper(), "Others"))
        
        return df.dropna()
    except Exception as e:
        st.error(f"Error fetching data from TradingView: {e}")
        return pd.DataFrame()

def calculate_gain(minutes, current_time_str, segment_filter="All Stocks"):
    conn = sqlite3.connect(DB_NAME)
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    target_str = (curr_dt - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    
    df_curr = pd.read_sql_query("SELECT symbol, rel_vol, change_pct, sector_index FROM relvol_snapshots WHERE timestamp = ?", conn, params=(current_time_str,))
    if df_curr.empty:
        conn.close()
        return pd.DataFrame(), f'+{minutes}m Gain'

    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (target_str,))
    past_row = cursor.fetchone()
    if not past_row:
        cursor.execute("SELECT MIN(timestamp) FROM relvol_snapshots")
        past_row = cursor.fetchone()

    if not past_row or not past_row[0]:
        conn.close()
        return pd.DataFrame(), f'+{minutes}m Gain'

    df_past = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(past_row[0],))
    conn.close()

    # Merge current and past data
    merged = pd.merge(df_curr, df_past, on='symbol', suffixes=('_now', '_past'))
    merged['Gain'] = merged['rel_vol_now'] - merged['rel_vol_past']
    
    # Tag F&O / Cash segment
    merged['Segment'] = merged['symbol'].apply(lambda s: "⚡ F&O" if s.upper() in FNO_STOCKS else "Cash")

    # Apply Segment Filter
    if segment_filter == "F&O Stocks Only":
        merged = merged[merged['Segment'] == "⚡ F&O"]
    elif segment_filter == "Cash Stocks Only":
        merged = merged[merged['Segment'] == "Cash"]

    # Sort descending by relative volume gain and pick top 10
    top = merged.sort_values(by='Gain', ascending=False).head(10).copy()
    
    # TradingView Chart Link
    top['TradingView Chart'] = top['symbol'].apply(
        lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}"
    )

    # Reorder columns
    top = top[['symbol', 'sector_index', 'TradingView Chart', 'Segment', 'change_pct', 'rel_vol_now', 'Gain']].copy()
    
    # Format numbers
    top['rel_vol_now'] = top['rel_vol_now'].round(2)
    top['Gain'] = top['Gain'].round(2)
    top['change_pct'] = top['change_pct'].round(2)
    
    # Rename columns
    gain_col_name = f'+{minutes}m Gain'
    top.columns = ['Symbol', 'Sector Index', 'TradingView Chart', 'Segment', 'Price Change %', 'Current Rel Vol', gain_col_name]
    return top.reset_index(drop=True), gain_col_name

# ==========================================
# COLOR HIGHLIGHT FUNCTION
# ==========================================
def style_price_change(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: #00c853; font-weight: bold;'  # Bright Green
        elif val < 0:
            return 'color: #ff1744; font-weight: bold;'  # Bright Red
    return ''

# ==========================================
# DASHBOARD UI
# ==========================================
init_db()
now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

# Fetch and store current minute data
live_df = fetch_live_data()
if not live_df.empty:
    save_snapshot(live_df, now_str)

st.title("📈 TradingView Relative Volume Tracker")
st.caption(f"Last updated: {now_str} IST (Auto-refreshes every 60 seconds)")

# Sidebar Segment Selector
st.sidebar.header("Filter Options")
selected_segment = st.sidebar.radio(
    "Select Stock Segment:",
    options=["All Stocks", "F&O Stocks Only", "Cash Stocks Only"],
    index=0
)

# Timeframe Selector Tabs
tab1, tab3, tab5, tab10, tab15 = st.tabs(["1 Min", "3 Min", "5 Min", "10 Min", "15 Min"])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 10 Gainers - Last {mins} Minute(s)")
        df_gain, gain_col_name = calculate_gain(mins, now_str, segment_filter=selected_segment)
        
        if not df_gain.empty:
            # Apply color mapping style to 'Price Change %' column
            styled_df = df_gain.style.map(
                style_price_change, 
                subset=['Price Change %']
            ).format({
                'Price Change %': '{:+.2f}%'
            })

            # Render dataframe with ALL columns center-aligned
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn(
                        "Chart Link", 
                        display_text="📈 Open Chart",
                        alignment="center"
                    ),
                    "Segment": st.column_config.Column(alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "Current Rel Vol": st.column_config.Column(alignment="center"),
                    gain_col_name: st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("Accumulating historical data... Please wait a few minutes.")
import pandas as pd
import requests
from tradingview_screener import Query, col

def get_nifty_500_csv():
    """Fetch Nifty 500 constituents directly from NSE's official CSV source."""
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            return df['Symbol'].tolist()
    except Exception as e:
        print(f"Error fetching Nifty 500: {e}")
    return []

def get_fno_stocks_tradingview():
    """Fetch live FnO stock universe dynamically from TradingView Screener API."""
    try:
        # Screen India stock market for contracts with options available
        q = (Query()
             .set_markets('india')
             .select('name', 'description', 'close')
             .where(col('has_options') == True)
             .get_scanner_data())
        
        fno_df = q[1]  # Extracting DataFrame from scanner output
        return fno_df['name'].tolist()
    except Exception as e:
        print(f"Error fetching FnO list: {e}")
        return []

if __name__ == "__main__":
    print("Fetching live Nifty 500 stock list...")
    nifty_500 = get_nifty_500_csv()
    print(f"Total Nifty 500 stocks fetched: {len(nifty_500)}")

    print("\nFetching live FnO stock list...")
    fno_list = get_fno_stocks_tradingview()
    print(f"Total FnO stocks fetched: {len(fno_list)}")

    # Save to dynamic CSV files
    pd.DataFrame({"Nifty500_Symbol": nifty_500}).to_csv("nifty_500_live.csv", index=False)
    pd.DataFrame({"FnO_Symbol": fno_list}).to_csv("fno_stocks_live.csv", index=False)
    print("\nUpdated lists saved locally as CSV files successfully!")