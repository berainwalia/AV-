import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
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

FNO_STOCKS = set(SECTOR_INDEX_MAP.keys())

st.set_page_config(page_title="TradingView RelVol Dashboard", layout="wide")

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
        df['Sector Index'] = df['Symbol'].apply(lambda s: SECTOR_INDEX_MAP.get(s.upper(), "Others"))
        return df.dropna()
    except Exception as e:
        st.error(f"Error fetching data from TradingView: {e}")
        return pd.DataFrame()

def calculate_gain_by_exact_timestamps(start_ts, end_ts, segment_filter="All Stocks", label_name="Gain"):
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
    merged['Segment'] = merged['symbol'].apply(lambda s: "⚡ F&O" if s.upper() in FNO_STOCKS else "Cash")

    if segment_filter == "F&O Stocks Only":
        merged = merged[merged['Segment'] == "⚡ F&O"]
    elif segment_filter == "Cash Stocks Only":
        merged = merged[merged['Segment'] == "Cash"]

    top = merged.sort_values(by='Gain', ascending=False).head(10).copy()
    top['TradingView Chart'] = top['symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    top = top[['symbol', 'sector_index', 'TradingView Chart', 'Segment', 'change_pct', 'rel_vol_end', 'Gain']].copy()
    top['rel_vol_end'] = top['rel_vol_end'].round(2)
    top['Gain'] = top['Gain'].round(2)
    top['change_pct'] = top['change_pct'].round(2)

    top.columns = ['Symbol', 'Sector Index', 'TradingView Chart', 'Segment', 'Price Change %', 'End Rel Vol', label_name]
    return top.reset_index(drop=True), label_name, actual_start_ts, actual_end_ts

def calculate_gain_relative(minutes, current_time_str, segment_filter="All Stocks"):
    curr_dt = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    start_str = (curr_dt - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    df, label, _, _ = calculate_gain_by_exact_timestamps(start_str, current_time_str, segment_filter, f'+{minutes}m Gain')
    return df, label

def fetch_day_movers(live_df, segment_filter="All Stocks"):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = live_df.copy()
    df['Segment'] = df['Symbol'].apply(lambda s: "⚡ F&O" if s.upper() in FNO_STOCKS else "Cash")

    if segment_filter == "F&O Stocks Only":
        df = df[df['Segment'] == "⚡ F&O"]
    elif segment_filter == "Cash Stocks Only":
        df = df[df['Segment'] == "Cash"]

    df['TradingView Chart'] = df['Symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    # Top Day Gainers: Positive price change, sorted by Relative Volume
    gainers = df[df['ChangePct'] > 0].sort_values(by='RelVol', ascending=False).head(10).copy()
    
    # Top Day Losers: Negative price change, sorted by Relative Volume
    losers = df[df['ChangePct'] < 0].sort_values(by='RelVol', ascending=False).head(10).copy()

    for target_df in [gainers, losers]:
        if not target_df.empty:
            target_df['RelVol'] = target_df['RelVol'].round(2)
            target_df['ChangePct'] = target_df['ChangePct'].round(2)

    cols_order = ['Symbol', 'Sector Index', 'TradingView Chart', 'Segment', 'ChangePct', 'RelVol']
    col_names = ['Symbol', 'Sector Index', 'TradingView Chart', 'Segment', 'Price Change %', 'Day Rel Vol']

    if not gainers.empty:
        gainers = gainers[cols_order]
        gainers.columns = col_names

    if not losers.empty:
        losers = losers[cols_order]
        losers.columns = col_names

    return gainers.reset_index(drop=True), losers.reset_index(drop=True)

def style_price_change(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: #00c853; font-weight: bold;'
        elif val < 0:
            return 'color: #ff1744; font-weight: bold;'
    return ''

# ==========================================
# 5-MINUTE STEP TIME OPTIONS GENERATOR (09:15 to 15:30)
# ==========================================
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
# DASHBOARD UI & EXECUTION
# ==========================================
init_db()

now_dt = datetime.now(TIMEZONE)
now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now_dt.strftime("%Y-%m-%d")

check_and_reset_daily(today_date_str)

live_df = fetch_live_data()
if not live_df.empty:
    save_snapshot(live_df, now_str)

st.title("📈 TradingView Relative Volume Tracker")
st.caption(f"Last updated: {now_str} IST (Auto-refreshes every 60 seconds)")

# Sidebar Segment Filter
st.sidebar.header("Filter Options")
selected_segment = st.sidebar.radio(
    "Select Stock Segment:",
    options=["All Stocks", "F&O Stocks Only", "Cash Stocks Only"],
    index=0
)

# Custom Time Range Picker
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Custom Time Range")

time_options = generate_5min_time_options()
time_labels = [opt[0] for opt in time_options]

selected_start_label = st.sidebar.selectbox(
    "Select Start Time:",
    options=time_labels,
    index=0  # Defaults to 09:15 AM
)

start_idx = time_labels.index(selected_start_label)
default_end_idx = min(start_idx + 1, len(time_labels) - 1)

selected_end_label = st.sidebar.selectbox(
    "Select End Time:",
    options=time_labels,
    index=default_end_idx  # Defaults to 09:20 AM
)

custom_start_time = next(opt[1] for opt in time_options if opt[0] == selected_start_label)
custom_end_time = next(opt[1] for opt in time_options if opt[0] == selected_end_label)

if st.sidebar.button("🧹 Reset Snapshot Database"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relvol_snapshots")
    conn.commit()
    conn.close()
    st.sidebar.success("Database cleared!")
    st.rerun()

# Timeframe Tabs
tab1, tab3, tab5, tab10, tab15, tab_custom, tab_day = st.tabs([
    "1 Min", "3 Min", "5 Min", "10 Min", "15 Min", "🎯 Custom Range", "🔥 Day Gainers/Losers"
])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 10 Gainers - Last {mins} Minute(s)")
        df_gain, gain_col_name = calculate_gain_relative(mins, now_str, segment_filter=selected_segment)
        
        if not df_gain.empty:
            styled_df = df_gain.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Segment": st.column_config.Column(alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "End Rel Vol": st.column_config.Column(alignment="center"),
                    gain_col_name: st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("Accumulating data... Please wait a few minutes.")

# Custom Range Tab Execution
with tab_custom:
    st.subheader(f"Top Gainers: {selected_start_label} ➔ {selected_end_label}")
    
    if custom_start_time >= custom_end_time:
        st.warning("⚠️ Please select an **End Time** that is strictly after the **Start Time**.")
    else:
        start_ts_str = f"{today_date_str} {custom_start_time.strftime('%H:%M:%S')}"
        end_ts_str = f"{today_date_str} {custom_end_time.strftime('%H:%M:%S')}"
        
        df_custom, gain_col_name, act_start, act_end = calculate_gain_by_exact_timestamps(
            start_ts_str, 
            end_ts_str, 
            segment_filter=selected_segment, 
            label_name="Custom Window Gain"
        )
        
        if not df_custom.empty:
            st.caption(f"Comparing database snapshots from `{act_start.split(' ')[1]}` to `{act_end.split(' ')[1]}`.")
            styled_custom = df_custom.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_custom, 
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Segment": st.column_config.Column(alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "End Rel Vol": st.column_config.Column(alignment="center"),
                    gain_col_name: st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info(f"No snapshot data recorded between {selected_start_label} and {selected_end_label} yet. Keep Streamlit running during market hours to log snapshots.")

# Day Gainers/Losers Tab Execution
with tab_day:
    st.subheader("🔥 Top Day Gainers & Losers (Sorted by Relative Volume)")
    
    gainers_df, losers_df = fetch_day_movers(live_df, segment_filter=selected_segment)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Top Day Gainers")
        if not gainers_df.empty:
            styled_gainers = gainers_df.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_gainers,
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Segment": st.column_config.Column(alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "Day Rel Vol": st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("No day gainers found matching current filter.")

    with col2:
        st.markdown("### 🔴 Top Day Losers")
        if not losers_df.empty:
            styled_losers = losers_df.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_losers,
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Segment": st.column_config.Column(alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "Day Rel Vol": st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("No day losers found matching current filter.")
