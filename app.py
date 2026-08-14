import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query
from streamlit_autorefresh import st_autorefresh

# ==========================================
# CONFIGURATION & SECTOR MAPPINGS
# ==========================================
DB_NAME = "relvol_fno_history.db"
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Master F&O list mapping (223 Stocks)
FNO_SECTOR_MAP = {
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
    "ZYDUSLIFE": "NIFTY Healthcare",
}

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

# Custom CSS for compact table columns & eliminating horizontal scrolling
st.markdown("""
    <style>
    .stDataFrame table {
        font-size: 12px !important;
    }
    div[data-testid="stTable"] {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# Auto-refresh app every 60 seconds (60,000 ms)
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
# AUTOMATED DYNAMIC DATA FETCHING
# ==========================================
def fetch_live_fno_data(universe_type="FnO"):
    try:
        q = Query().set_markets('india').select('name', 'relative_volume_10d_calc', 'change', 'sector')
        
        if universe_type == "FnO":
            q = q.limit(400)
        else:
            q = q.order_by('market_cap_basic', ascending=False).limit(500)
            
        df = q.get_scanner_data()
        if isinstance(df, tuple):
            df = df[1]

        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector']].dropna(subset=['name', 'relative_volume_10d_calc', 'change'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector']
        
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        
        if universe_type == "FnO":
            valid_symbols = set(FNO_SECTOR_MAP.keys())
            df = df[df['Symbol'].isin(valid_symbols)].copy()
            df['Sector Index'] = df['Symbol'].map(FNO_SECTOR_MAP)
        else:
            df['Sector Index'] = df['Symbol'].map(FNO_SECTOR_MAP).fillna(df['TV Sector'].fillna("Other"))

        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        
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

def fetch_day_movers_with_tf_comparison(live_df, current_time_str):
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
    
    df['+1m'] = df.apply(lambda r: round(r['RelVol'] - vol_1m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+3m'] = df.apply(lambda r: round(r['RelVol'] - vol_3m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+5m'] = df.apply(lambda r: round(r['RelVol'] - vol_5m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+10m'] = df.apply(lambda r: round(r['RelVol'] - vol_10m.get(r['Symbol'], r['RelVol']), 2), axis=1)
    df['+15m'] = df.apply(lambda r: round(r['RelVol'] - vol_15m.get(r['Symbol'], r['RelVol']), 2), axis=1)

    gainers = df.sort_values(by='ChangePct', ascending=False).head(10).copy()
    losers = df.sort_values(by='ChangePct', ascending=True).head(10).copy()

    cols_order = ['Symbol', 'TradingView Chart', 'ChangePct', 'RelVol', '+1m', '+3m', '+5m', '+10m', '+15m']
    col_names = ['Symbol', 'Chart', 'Chg %', 'RVol', '+1m', '+3m', '+5m', '+10m', '+15m']

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
# DASHBOARD INITIALIZATION & AUTOMATION
# ==========================================
init_db()

now_dt = datetime.now(TIMEZONE)
now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now_dt.strftime("%Y-%m-%d")

check_and_reset_daily(today_date_str)

# Sidebar Options
st.sidebar.header("🎯 Stock Universe Selection")
universe_choice = st.sidebar.radio(
    "Select Universe:",
    options=["FnO Stocks (223)", "Nifty 500 Stocks"],
    index=0
)
selected_universe = "FnO" if "FnO" in universe_choice else "Nifty500"

# Fetch & Save snapshot every minute automatically
live_df = fetch_live_fno_data(universe_type=selected_universe)
if not live_df.empty:
    save_snapshot(live_df, now_str)

st.title("⚡ NSE Relative Volume & Price Movers Tracker")
st.caption(f"Tracking: **{universe_choice} ({len(live_df)} Symbols)** | Last updated: **{now_str} IST** | 🔄 *Automated minute snapshots active*")

# Manual Override Trigger
if st.sidebar.button("⚡ Force Snapshot Now"):
    live_df = fetch_live_fno_data(universe_type=selected_universe)
    if not live_df.empty:
        save_snapshot(live_df, now_str)
    st.sidebar.success("Snapshot manually recorded!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Custom Time Range")

time_options = generate_5min_time_options()
time_labels = [opt[0] for opt in time_options]

selected_start_label = st.sidebar.selectbox("Start Time:", options=time_labels, index=0)
start_idx = time_labels.index(selected_start_label)
default_end_idx = min(start_idx + 1, len(time_labels) - 1)

selected_end_label = st.sidebar.selectbox("End Time:", options=time_labels, index=default_end_idx)

custom_start_time = next(opt[1] for opt in time_options if opt[0] == selected_start_label)
custom_end_time = next(opt[1] for opt in time_options if opt[0] == selected_end_label)

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
    "1 Min", "3 Min", "5 Min", "10 Min", "15 Min", "🎯 Custom Range", "🔥 Top Gainers/Losers"
])

for tab, mins in zip([tab1, tab3, tab5, tab10, tab15], [1, 3, 5, 10, 15]):
    with tab:
        st.subheader(f"Top 10 Volume Gainers - Last {mins} Minute(s)")
        df_rel, label_name = calculate_gain_relative(mins, now_str)
        if not df_rel.empty:
            st.dataframe(
                df_rel.style.map(style_price_change, subset=['Price Change %']),
                column_config={"TradingView Chart": st.column_config.LinkColumn("Chart", display_text="Chart")},
                use_container_width=True
            )
        else:
            st.info("Accumulating minute snapshot data for this interval...")

with tab_custom:
    st.subheader("Top Volume Gainers - Custom Time Window")
    start_str = f"{today_date_str} {custom_start_time.strftime('%H:%M:%S')}"
    end_str = f"{today_date_str} {custom_end_time.strftime('%H:%M:%S')}"
    
    df_custom, label, act_start, act_end = calculate_gain_by_exact_timestamps(start_str, end_str, "Custom Range Gain")
    if not df_custom.empty:
        st.caption(f"Comparing snapshot from **{act_start}** to **{act_end}**")
        st.dataframe(
            df_custom.style.map(style_price_change, subset=['Price Change %']),
            column_config={"TradingView Chart": st.column_config.LinkColumn("Chart", display_text="Chart")},
            use_container_width=True
        )
    else:
        st.info("No snapshots recorded for the selected custom timeframe yet.")

with tab_day:
    st.subheader("Day's Top Price Gainers & Losers with Multi-Timeframe Volume Gains")
    gainers, losers = fetch_day_movers_with_tf_comparison(live_df, now_str)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 Top 10 Price Gainers")
        if not gainers.empty:
            st.dataframe(
                gainers.style.map(style_price_change, subset=['Chg %']),
                column_config={
                    "Chart": st.column_config.LinkColumn("Chart", display_text="Open"),
                    "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
                    "Chg %": st.column_config.NumberColumn("Chg %", width="small"),
                    "RVol": st.column_config.NumberColumn("RVol", width="small"),
                    "+1m": st.column_config.NumberColumn("+1m", width="small"),
                    "+3m": st.column_config.NumberColumn("+3m", width="small"),
                    "+5m": st.column_config.NumberColumn("+5m", width="small"),
                    "+10m": st.column_config.NumberColumn("+10m", width="small"),
                    "+15m": st.column_config.NumberColumn("+15m", width="small"),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No data available.")

    with col2:
        st.markdown("### 🔴 Top 10 Price Losers")
        if not losers.empty:
            st.dataframe(
                losers.style.map(style_price_change, subset=['Chg %']),
                column_config={
                    "Chart": st.column_config.LinkColumn("Chart", display_text="Open"),
                    "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
                    "Chg %": st.column_config.NumberColumn("Chg %", width="small"),
                    "RVol": st.column_config.NumberColumn("RVol", width="small"),
                    "+1m": st.column_config.NumberColumn("+1m", width="small"),
                    "+3m": st.column_config.NumberColumn("+3m", width="small"),
                    "+5m": st.column_config.NumberColumn("+5m", width="small"),
                    "+10m": st.column_config.NumberColumn("+10m", width="small"),
                    "+15m": st.column_config.NumberColumn("+15m", width="small"),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No data available.")
