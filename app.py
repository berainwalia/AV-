import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from tradingview_screener import Query
from streamlit_autorefresh import st_autorefresh

# ==========================================
# CONFIGURATION & F&O STOCK LIST
# ==========================================
DB_NAME = "relvol_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Set of active NSE F&O stock symbols
FNO_STOCKS = {
    "AARTIIND", "ABB", "ABFRL", "ABBOTINDIA", "ACC", "ADANIENT", "ADANIPORTS", 
    "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", 
    "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", 
    "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", 
    "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", 
    "BPCL", "BRITANNIA", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", 
    "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", 
    "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPACKNTR", "DIVISLAB", "DIXON", "DLF", 
    "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK", 
    "GMRAIRPORT", "GNFC", "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD", "HAL", 
    "HAVELLS", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", 
    "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", 
    "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIAMART", "INDIGO", 
    "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC", "IRFC", "ITC", 
    "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KALYANKJWR", "KEI", 
    "KOTAKBANK", "LALPATHLAB", "LT", "LTIM", "LTF", "LTI", "LTTS", "LUPIN", 
    "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MCX", 
    "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", 
    "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", 
    "OFSS", "ONGC", "PAGEIND", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", 
    "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", 
    "RECLTD", "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", 
    "SHRIRAMFIN", "SIEMENS", "SLA", "SRF", "SUNPHARMA", "SUNTV", "SYNGENE", 
    "TATACOMM", "TATACONSUM", "TATEL", "TATAMOTORS", "TATAPOWER", "TATASTEEL", 
    "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", 
    "UBL", "ULTRACEMCO", "UPL", "VDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE"
}

st.set_page_config(page_title="TradingView RelVol Dashboard", layout="wide")

# Automatically refresh the dashboard every 60 seconds
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
            PRIMARY KEY (timestamp, symbol)
        )
    """)
    conn.commit()
    conn.close()

def save_snapshot(df, now_str):
    if df.empty:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data = [
        (now_str, row['Symbol'], float(row['RelVol']), float(row['ChangePct'])) 
        for _, row in df.iterrows()
    ]
    cursor.executemany("INSERT OR REPLACE INTO relvol_snapshots VALUES (?, ?, ?, ?)", data)
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
        return df.dropna()
    except Exception as e:
        st.error(f"Error fetching data from TradingView: {e}")
        return pd.DataFrame()

def calculate_gain(minutes, current_time_str, fno_only_filter=False):
    conn = sqlite3.connect(DB_NAME)
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    target_str = (curr_dt - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    
    df_curr = pd.read_sql_query("SELECT symbol, rel_vol, change_pct FROM relvol_snapshots WHERE timestamp = ?", conn, params=(current_time_str,))
    if df_curr.empty:
        conn.close()
        return pd.DataFrame()

    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (target_str,))
    past_row = cursor.fetchone()
    if not past_row:
        cursor.execute("SELECT MIN(timestamp) FROM relvol_snapshots")
        past_row = cursor.fetchone()

    if not past_row or not past_row[0]:
        conn.close()
        return pd.DataFrame()

    df_past = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(past_row[0],))
    conn.close()

    # Merge current and past data on symbol
    merged = pd.merge(df_curr, df_past, on='symbol', suffixes=('_now', '_past'))
    merged['Gain'] = merged['rel_vol_now'] - merged['rel_vol_past']
    
    # Tag F&O stocks
    merged['Segment'] = merged['symbol'].apply(lambda s: "⚡ F&O" if s.upper() in FNO_STOCKS else "Cash")

    # Optional Filter: Show only F&O stocks
    if fno_only_filter:
        merged = merged[merged['Segment'] == "⚡ F&O"]

    # Sort descending by relative volume gain and pick top 10
    top = merged.sort_values(by='Gain', ascending=False).head(10).copy()
    
    # Construct TradingView Chart URL for each symbol
    top['TradingView Chart'] = top['symbol'].apply(
        lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}"
    )

    # Select and order columns to display
    top = top[['symbol', 'TradingView Chart', 'Segment', 'change_pct', 'rel_vol_now', 'Gain']].copy()
    
    # Format numbers
    top['rel_vol_now'] = top['rel_vol_now'].round(2)
    top['Gain'] = top['Gain'].round(2)
    top['change_pct'] = top['change_pct'].round(2)
    top['change_pct'] = top['change_pct'].apply(lambda x: f"+{x}%" if x > 0 else f"{x}%")
    
    # Rename columns
    top.columns = ['Symbol', 'TradingView Chart', 'Segment', 'Price Change %', 'Current Rel Vol', f'+{minutes}m Gain']
    return top.reset_index(drop=True)

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

# Sidebar Filter
st.sidebar.header("Filter Options")
show_fno_only = st.sidebar.checkbox("Show ONLY F&O Stocks", value=False)

# Timeframe Selector Tabs
tab1, tab3, tab5, tab10, tab15 = st.tabs(["1 Min", "3 Min", "5 Min", "10 Min", "15 Min"])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 10 Gainers - Last {mins} Minute(s)")
        df_gain = calculate_gain(mins, now_str, fno_only_filter=show_fno_only)
        if not df_gain.empty:
            st.dataframe(
                df_gain, 
                use_container_width=True,
                column_config={
                    "TradingView Chart": st.column_config.LinkColumn(
                        "Chart Link", 
                        display_text="📈 Open Chart"
                    )
                }
            )
        else:
            st.info("Accumulating historical data... Please wait a few minutes.")