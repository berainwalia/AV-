import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query, Column
from streamlit_autorefresh import st_autorefresh

# ==========================================
# CONFIGURATION & SECTOR MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Primary Sector mapping helper for core F&O Stocks
SECTOR_INDEX_MAP = {
    # BANKING & FINANCIALS
    "HDFCBANK": "NIFTY Bank", "ICICIBANK": "NIFTY Bank", "SBIN": "NIFTY Bank",
    "AXISBANK": "NIFTY Bank", "KOTAKBANK": "NIFTY Bank", "INDUSINDBK": "NIFTY Bank",
    "BANKBARODA": "NIFTY Bank", "PNB": "NIFTY Bank", "CANBK": "NIFTY Bank",
    "AUBANK": "NIFTY Bank", "FEDERALBNK": "NIFTY Bank", "IDFCFIRSTB": "NIFTY Bank",
    "BANDHANBNK": "NIFTY Bank", "RBLBANK": "NIFTY Bank", "BANKINDIA": "NIFTY Bank",
    "BAJFINANCE": "NIFTY Fin Service", "BAJAJFINSV": "NIFTY Fin Service", "CHOLAFIN": "NIFTY Fin Service", 
    "PFC": "NIFTY Fin Service", "RECLTD": "NIFTY Fin Service", "SHRIRAMFIN": "NIFTY Fin Service", 
    "MUTHOOTFIN": "NIFTY Fin Service", "SBILIFE": "NIFTY Fin Service", "HDFCLIFE": "NIFTY Fin Service", 
    "ICICIPRULI": "NIFTY Fin Service", "ICICIGI": "NIFTY Fin Service", "MCX": "NIFTY Fin Service",
    "BSE": "NIFTY Fin Service", "CDSL": "NIFTY Fin Service", "CAMS": "NIFTY Fin Service",
    "ANGELONE": "NIFTY Fin Service", "360ONE": "NIFTY Fin Service", "LICHSGFIN": "NIFTY Fin Service",
    "M&MFIN": "NIFTY Fin Service", "MANAPPURAM": "NIFTY Fin Service", "HDFCAMC": "NIFTY Fin Service",
    "SBICARD": "NIFTY Fin Service", "MAXHEALTH": "NIFTY Fin Service",

    # IT & TECH
    "TCS": "NIFTY IT", "INFY": "NIFTY IT", "HCLTECH": "NIFTY IT",
    "WIPRO": "NIFTY IT", "TECHM": "NIFTY IT", "LTIM": "NIFTY IT",
    "PERSISTENT": "NIFTY IT", "COFORGE": "NIFTY IT", "MPHASIS": "NIFTY IT",
    "LTTS": "NIFTY IT", "BSOFT": "NIFTY IT", "OFSS": "NIFTY IT", "TATAELXSI": "NIFTY IT",

    # AUTOMOBILE & AUTO ANCILLARIES
    "TATAMOTORS": "NIFTY Auto", "M&M": "NIFTY Auto", "MARUTI": "NIFTY Auto",
    "BAJAJ-AUTO": "NIFTY Auto", "EICHERMOT": "NIFTY Auto", "HEROMOTOCO": "NIFTY Auto",
    "TVSMOTOR": "NIFTY Auto", "ASHOKLEY": "NIFTY Auto", "BHARATFORG": "NIFTY Auto",
    "BALKRISIND": "NIFTY Auto", "MRF": "NIFTY Auto", "MOTHERSON": "NIFTY Auto",
    "APOLLOTYRE": "NIFTY Auto", "ESCORTS": "NIFTY Auto", "BOSCHLTD": "NIFTY Auto",
    "TIINDIA": "NIFTY Auto", "EXIDEIND": "NIFTY Auto",

    # PHARMA & HEALTHCARE
    "SUNPHARMA": "NIFTY Pharma", "CIPLA": "NIFTY Pharma", "DRREDDY": "NIFTY Pharma",
    "DIVISLAB": "NIFTY Pharma", "ZYDUSLIFE": "NIFTY Pharma", "TORNTPHARM": "NIFTY Pharma",
    "LUPIN": "NIFTY Pharma", "AUROPHARMA": "NIFTY Pharma", "ALKEM": "NIFTY Pharma",
    "GLENMARK": "NIFTY Pharma", "BIOCON": "NIFTY Pharma", "IPCALAB": "NIFTY Pharma",
    "APOLLOHOSP": "NIFTY Healthcare", "LALPATHLAB": "NIFTY Healthcare", "METROPOLIS": "NIFTY Healthcare",
    "SYNGENE": "NIFTY Healthcare", "GRANULES": "NIFTY Pharma", "ABBOTINDIA": "NIFTY Pharma",
    "LAURUSLABS": "NIFTY Pharma", "FORTIS": "NIFTY Healthcare", "MANKIND": "NIFTY Pharma",

    # METALS & MINING
    "TATASTEEL": "NIFTY Metal", "JSWSTEEL": "NIFTY Metal", "HINDALCO": "NIFTY Metal",
    "JINDALSTEL": "NIFTY Metal", "VEDL": "NIFTY Metal", "NMDC": "NIFTY Metal", 
    "SAIL": "NIFTY Metal", "NATIONALUM": "NIFTY Metal", "HINDCOPPER": "NIFTY Metal",
    "APLAPOLLO": "NIFTY Metal", "JSL": "NIFTY Metal",

    # CONSUMER GOODS, FMCG & RETAIL
    "ITC": "NIFTY FMCG", "HINDUNILVR": "NIFTY FMCG", "BRITANNIA": "NIFTY FMCG",
    "NESTLEIND": "NIFTY FMCG", "DABUR": "NIFTY FMCG", "GODREJCP": "NIFTY FMCG",
    "MARICO": "NIFTY FMCG", "COLPAL": "NIFTY FMCG", "TATACONSUM": "NIFTY FMCG",
    "UNITDSPR": "NIFTY FMCG", "UBL": "NIFTY FMCG", "BALRAMCHIN": "NIFTY FMCG",
    "VBL": "NIFTY FMCG", "TRENT": "NIFTY Retail", "ABFRL": "NIFTY Retail",
    "JUBLFOOD": "NIFTY Retail", "DMART": "NIFTY Retail", "NYKAA": "NIFTY Retail",

    # ENERGY, OIL & GAS, POWER
    "RELIANCE": "NIFTY Oil & Gas", "ONGC": "NIFTY Oil & Gas", "IOC": "NIFTY Oil & Gas",
    "BPCL": "NIFTY Oil & Gas", "HPCL": "NIFTY Oil & Gas", "HINDPETRO": "NIFTY Oil & Gas",
    "GAIL": "NIFTY Oil & Gas", "PETRONET": "NIFTY Oil & Gas", "IGL": "NIFTY Oil & Gas",
    "MGL": "NIFTY Oil & Gas", "GUJGASLTD": "NIFTY Oil & Gas", "NTPC": "NIFTY Power",
    "POWERGRID": "NIFTY Power", "TATAPOWER": "NIFTY Power", "COALINDIA": "NIFTY Energy",
    "ADANIENT": "NIFTY Energy", "ADANIPORTS": "NIFTY Infra", "ADANIGREEN": "NIFTY Power",
    "ADANIPOWER": "NIFTY Power", "ADANIENSOL": "NIFTY Power", "OIL": "NIFTY Oil & Gas",

    # CAPITAL GOODS, INFRA & DEFENCE
    "LT": "NIFTY Infra", "HAL": "NIFTY Defence", "BEL": "NIFTY Defence", "BDL": "NIFTY Defence",
    "BHEL": "NIFTY Infra", "SIEMENS": "NIFTY Infra", "ABB": "NIFTY Infra",
    "CUMMINSIND": "NIFTY Infra", "CONCOR": "NIFTY Infra", "CGPOWER": "NIFTY Infra",
    "IRCTC": "NIFTY Infra", "IRFC": "NIFTY Infra", "COCHINSHIP": "NIFTY Defence",
    "MAZDOCK": "NIFTY Defence", "POLYCAB": "NIFTY Infra", "KEI": "NIFTY Infra",

    # REALTY & OTHERS
    "DLF": "NIFTY Realty", "GODREJPROP": "NIFTY Realty", "OBEROIRLTY": "NIFTY Realty",
    "PHOENIXLTD": "NIFTY Realty", "TITAN": "NIFTY Consumer Durables", "HAVELLS": "NIFTY Consumer Durables",
    "VOLTAS": "NIFTY Consumer Durables", "CROMPTON": "NIFTY Consumer Durables", "DIXON": "NIFTY Consumer Durables",
    "ASTRAL": "NIFTY Infra", "ASIANPAINT": "NIFTY Consumer Durables", "BERGEPAINT": "NIFTY Consumer Durables",
    "PIDILITIND": "NIFTY Chemicals", "SRF": "NIFTY Chemicals", "UPL": "NIFTY Chemicals",
    "DEEPAKNTR": "NIFTY Chemicals", "PIIND": "NIFTY Chemicals", "AMBUJACEM": "NIFTY Infra",
    "ACC": "NIFTY Infra", "ULTRACEMCO": "NIFTY Infra", "DALBHARAT": "NIFTY Infra",
    "SHREECEM": "NIFTY Infra", "GMRINFRA": "NIFTY Infra"
}

st.set_page_config(page_title="NSE F&O Relative Volume Tracker", layout="wide")

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
# DYNAMIC F&O SCANNER FETCHING
# ==========================================
@st.cache_data(ttl=300)
def fetch_live_fno_data():
    """Dynamically fetches all current NSE F&O stocks directly from TradingView API."""
    try:
        # Filter for India exchange stocks having active derivatives (F&O tradable)
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'sector')
            .where(
                Column('typespecs').has('derivatives')  # Automatically includes all F&O segment stocks
            )
            .limit(300)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]
            
        if df is None or df.empty:
            # Fallback query if 'derivatives' spec filter yields no results
            df = (
                Query()
                .set_markets('india')
                .select('name', 'relative_volume_10d_calc', 'change', 'sector')
                .limit(300)
                .get_scanner_data()
            )
            if isinstance(df, tuple):
                df = df[1]

        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector']].dropna(subset=['name', 'relative_volume_10d_calc', 'change'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector']
        
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        
        # Sector Auto-Assignment Logic
        def get_sector(symbol, tv_sector):
            sym_upper = symbol.upper()
            if sym_upper in SECTOR_INDEX_MAP:
                return SECTOR_INDEX_MAP[sym_upper]
            elif pd.notna(tv_sector) and str(tv_sector).strip() != "":
                return f"NIFTY {str(tv_sector).title()}"
            return "NIFTY F&O Other"

        df['Sector Index'] = df.apply(lambda row: get_sector(row['Symbol'], row['TV Sector']), axis=1)
        
        return df.dropna(subset=['RelVol', 'ChangePct']).reset_index(drop=True)

    except Exception as e:
        st.error(f"Error dynamically pulling F&O stock updates from TradingView: {e}")
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

    top = merged.sort_values(by='Gain', ascending=False).head(10).copy()
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

def fetch_day_movers(live_df):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = live_df.copy()
    df['TradingView Chart'] = df['Symbol'].apply(lambda s: f"https://in.tradingview.com/chart/?symbol=NSE:{s}")

    # Ranked Strictly by Percentage Gain (Highest % First)
    gainers = df.sort_values(by='ChangePct', ascending=False).head(10).copy()
    
    # Ranked Strictly by Percentage Loss (Most Negative % First)
    losers = df.sort_values(by='ChangePct', ascending=True).head(10).copy()

    for target_df in [gainers, losers]:
        if not target_df.empty:
            target_df['RelVol'] = target_df['RelVol'].round(2)
            target_df['ChangePct'] = target_df['ChangePct'].round(2)

    cols_order = ['Symbol', 'Sector Index', 'TradingView Chart', 'ChangePct', 'RelVol']
    col_names = ['Symbol', 'Sector Index', 'TradingView Chart', 'Price Change %', 'Relative Volume']

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
# DASHBOARD INITIALIZATION & UI
# ==========================================
init_db()

now_dt = datetime.now(TIMEZONE)
now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now_dt.strftime("%Y-%m-%d")

check_and_reset_daily(today_date_str)

# Fetch Live F&O Stocks directly
live_df = fetch_live_fno_data()
if not live_df.empty:
    save_snapshot(live_df, now_str)

st.title("⚡ NSE F&O Relative Volume & Price Movers")
st.caption(f"Showing **F&O Segment Only** | Last updated: {now_str} IST (Auto-refreshes every 60 seconds)")

# Sidebar Configuration
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

# Timeframe Tabs
tab1, tab3, tab5, tab10, tab15, tab_custom, tab_day = st.tabs([
    "1 Min", "3 Min", "5 Min", "10 Min", "15 Min", "🎯 Custom Range", "🔥 F&O Day Gainers/Losers"
])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 10 Volume Gainers (F&O) - Last {mins} Minute(s)")
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
            st.info("Accumulating intraday snapshot data... Please wait a few moments.")

# Custom Range Tab
with tab_custom:
    st.subheader(f"Top F&O RelVol Gainers: {selected_start_label} ➔ {selected_end_label}")
    
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

# F&O Day Gainers / Losers Tab
with tab_day:
    st.subheader("🔥 Top Day Gainers & Losers of F&O (By % Change & Relative Volume)")
    
    gainers_df, losers_df = fetch_day_movers(live_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Top F&O Day Gainers (% Increase)")
        if not gainers_df.empty:
            styled_gainers = gainers_df.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_gainers,
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "Relative Volume": st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("No day gainers available.")

    with col2:
        st.markdown("### 🔴 Top F&O Day Losers (% Drop)")
        if not losers_df.empty:
            styled_losers = losers_df.style.map(style_price_change, subset=['Price Change %']).format({'Price Change %': '{:+.2f}%'})
            st.dataframe(
                styled_losers,
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.Column(alignment="center"),
                    "Sector Index": st.column_config.Column(alignment="center"),
                    "TradingView Chart": st.column_config.LinkColumn("Chart Link", display_text="📈 Open Chart", alignment="center"),
                    "Price Change %": st.column_config.Column(alignment="center"),
                    "Relative Volume": st.column_config.Column(alignment="center")
                }
            )
        else:
            st.info("No day losers available.")
