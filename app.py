import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import pytz
from tradingview_screener import Query
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

st.set_page_config(page_title="NSE Relative Volume Tracker", layout="wide")

# UI Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="datarefresh")

# ==========================================
# FETCH PREVIOUS DAY HIGH & LOW LEVELS (YFINANCE)
# ==========================================
@st.cache_data(ttl=14400)
def fetch_pdh_pdl_levels():
    """Fetches Previous Day High and Previous Day Low via yfinance."""
    pdh_pdl_data = {}
    try:
        symbols = [f"{sym}.NS" for sym in VALID_SYMBOLS]
        data = yf.download(symbols, period="5d", interval="1d", progress=False)
        if not data.empty and "High" in data and "Low" in data:
            highs = data["High"]
            lows = data["Low"]
            for sym in VALID_SYMBOLS:
                ticker = f"{sym}.NS"
                try:
                    if ticker in highs.columns and ticker in lows.columns:
                        sym_highs = highs[ticker].dropna()
                        sym_lows = lows[ticker].dropna()
                        if len(sym_highs) >= 2 and len(sym_lows) >= 2:
                            pdh_pdl_data[sym] = {
                                "PDH": float(sym_highs.iloc[-2]),
                                "PDL": float(sym_lows.iloc[-2])
                            }
                except Exception:
                    continue
    except Exception as e:
        print(f"Error downloading PDH/PDL: {e}")
    return pdh_pdl_data

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
        
        # Pull name, relative volume, change, sector, high, and low levels
        df = (
            Query()
            .set_markets('india')
            .select('name', 'relative_volume_10d_calc', 'change', 'sector', 'high', 'low')
            .limit(limit)
            .get_scanner_data()
        )
        if isinstance(df, tuple):
            df = df[1]
        if df is None or df.empty:
            return pd.DataFrame()
            
        df = df[['name', 'relative_volume_10d_calc', 'change', 'sector', 'high', 'low']].dropna(subset=['name', 'relative_volume_10d_calc', 'change'])
        df.columns = ['Symbol', 'RelVol', 'ChangePct', 'TV Sector', 'High', 'Low']
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
        
        if stock_universe_mode == "Custom List":
            df = df[df['Symbol'].isin(VALID_SYMBOLS)].copy()
            
        df['RelVol'] = pd.to_numeric(df['RelVol'], errors='coerce')
        df['ChangePct'] = pd.to_numeric(df['ChangePct'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Sector Index'] = df['Symbol'].map(SECTOR_INDEX_MAP).fillna(df['TV Sector'].fillna("Other Sector"))
        
        # Add PDH and PDL Status
        pdh_pdl_dict = fetch_pdh_pdl_levels()
        
        pdh_status = []
        for _, row in df.iterrows():
            sym = row['Symbol']
            h = row['High']
            l = row['Low']
            levels = pdh_pdl_dict.get(sym, None)
            if levels and pd.notna(h) and pd.notna(l):
                pdh = levels['PDH']
                pdl = levels['PDL']
                if h > pdh:
                    pdh_status.append("PDH Cross 🟢")
                elif l < pdl:
                    pdh_status.append("PDL Cross 🔴")
                else:
                    pdh_status.append("Within Range ⚪")
            else:
                pdh_status.append("N/A ⚪")
                
        df['PDH/PDL Status'] = pdh_status
        
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
def get_past_relvol(minutes_ago):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    target_dt = datetime.now(TIMEZONE) - timedelta(minutes=minutes_ago)
    target_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT timestamp FROM relvol_snapshots WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (target_str,))
    p_row = cursor.fetchone()
    if p_row:
        p_df = pd.read_sql_query("SELECT symbol, rel_vol FROM relvol_snapshots WHERE timestamp = ?", conn, params=(p_row[0],))
        conn.close()
        return dict(zip(p_df['symbol'], p_df['rel_vol']))
    conn.close()
    return {}

def fetch_day_movers_with_multi_timeframes(live_df, now_str):
    if live_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    vol_1m = get_past_relvol(1)
    vol_3m = get_past_relvol(3)
    vol_5m = get_past_relvol(5)
    vol_10m = get_past_relvol(10)
    vol_15m = get_past_relvol(15)

    processed_rows = []
    for _, row in live_df.iterrows():
        sym = row['Symbol']
        c_vol = float(row['RelVol'])
        
        d1 = c_vol - vol_1m.get(sym, c_vol)
        d3 = c_vol - vol_3m.get(sym, c_vol)
        d5 = c_vol - vol_5m.get(sym, c_vol)
        d10 = c_vol - vol_10m.get(sym, c_vol)
        d15 = c_vol - vol_15m.get(sym, c_vol)

        tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{sym}"
        tv_link = f'<a href="{tv_url}" target="_blank">📈 Chart</a>'

        processed_rows.append({
            'Symbol': sym,
            'Sector Index': row.get('Sector Index', 'Other Sector'),
            'PDH/PDL Status': row.get('PDH/PDL Status', 'N/A ⚪'),
            'TradingView Chart': tv_link,
            'Price Change %': row['ChangePct'],
            'End Rel Vol': c_vol,
            '1m Gain': d1,
            '3m Gain': d3,
            '5m Gain': d5,
            '10m Gain': d10,
            '15m Gain': d15
        })

    full_df = pd.DataFrame(processed_rows)

    gainers = full_df[full_df['Price Change %'] >= 0].sort_values(by='End Rel Vol', ascending=False)
    losers = full_df[full_df['Price Change %'] < 0].sort_values(by='End Rel Vol', ascending=False)

    cols_order = [
        'Symbol', 'Sector Index', 'PDH/PDL Status', 'TradingView Chart', 'Price Change %', 
        'End Rel Vol', '1m Gain', '3m Gain', '5m Gain', '10m Gain', '15m Gain'
    ]

    valid_gain_cols = [c for c in cols_order if c in gainers.columns]
    valid_loss_cols = [c for c in cols_order if c in losers.columns]
    valid_full_cols = [c for c in cols_order if c in full_df.columns]

    return gainers[valid_gain_cols], losers[valid_loss_cols], full_df[valid_full_cols]

def style_price_change(val):
    if pd.isna(val):
        return ""
    color = "green" if val >= 0 else "red"
    return f"color: {color}; font-weight: bold;"

# Config for html links inside streamlit table
LINK_COLUMN_CONFIG = {
    "TradingView Chart": st.column_config.LinkColumn("TradingView Chart", display_text="📈 Chart")
}

# ==========================================
# STREAMLIT UI LAYOUT
# ==========================================
st.title("⚡ NSE Real-time Relative Volume & Price Tracker")

stock_universe = st.radio("Choose Stock Universe:", ["Custom List", "All F&O Stocks", "Nifty 500 Stocks"], horizontal=True)

live_df = fetch_live_fno_data(stock_universe)
now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

tab_movers, tab_indices, tab_sector_stocks = st.tabs([
    "🚀 Day Movers (FN&O)", 
    "📊 Sectoral & Thematic Indices", 
    "🔍 Sector-wise Stock Breakdown"
])

# ------------------------------------------
# TAB 1: DAY MOVERS
# ------------------------------------------
with tab_movers:
    st.subheader("🚀 Real-Time Day Movers & Multi-Timeframe Volume Dynamics")
    
    gainers_df, losers_df, _ = fetch_day_movers_with_multi_timeframes(live_df, now_str)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 Top Bullish Movers (Price Change ≥ 0%)")
        if not gainers_df.empty:
            styled_gainers = gainers_df.style.map(style_price_change, subset=["Price Change %"]).format({"Price Change %": "{:+.2f}%", "End Rel Vol": "{:.2f}"})
            st.dataframe(styled_gainers, column_config=LINK_COLUMN_CONFIG, use_container_width=True)
        else:
            st.info("No bullish movers detected.")

    with col2:
        st.markdown("### 🔴 Top Bearish Movers (Price Change < 0%)")
        if not losers_df.empty:
            styled_losers = losers_df.style.map(style_price_change, subset=["Price Change %"]).format({"Price Change %": "{:+.2f}%", "End Rel Vol": "{:.2f}"})
            st.dataframe(styled_losers, column_config=LINK_COLUMN_CONFIG, use_container_width=True)
        else:
            st.info("No bearish movers detected.")

# ------------------------------------------
# TAB 2: SECTOR & THEMATIC INDICES
# ------------------------------------------
with tab_indices:
    st.subheader("📊 Sectoral & Thematic Indices Relative Volume Tracking")

    if not live_df.empty:
        # Aggregate stock metrics by Sector Index
        indices_df = (
            live_df.groupby("Sector Index")
            .agg(
                Symbol=("Sector Index", "first"),
                RelVol=("RelVol", "mean"),
                ChangePct=("ChangePct", "mean"),
            )
            .reset_index(drop=True)
        )

        indices_df["Sector Index"] = indices_df["Symbol"]

        _, _, indices_tf_df = fetch_day_movers_with_multi_timeframes(indices_df, now_str)

        if not indices_tf_df.empty:
            indices_tf_df = indices_tf_df.drop(columns=["TradingView Chart", "Sector Index", "PDH/PDL Status"], errors="ignore")
            indices_tf_df = indices_tf_df.sort_values(by="End Rel Vol", ascending=False).reset_index(drop=True)

            styled_indices = indices_tf_df.style.map(
                style_price_change, subset=["Price Change %"]
            ).format({"Price Change %": "{:+.2f}%", "End Rel Vol": "{:.2f}"})

            st.dataframe(styled_indices, use_container_width=True)
        else:
            st.info("Accumulating multi-timeframe snapshot data for sector indices...")
    else:
        st.info("Loading sector relative volume data...")

# ------------------------------------------
# TAB 3: SECTOR-WISE BREAKDOWN
# ------------------------------------------
with tab_sector_stocks:
    st.subheader("🔍 Individual Sector Stock Breakdown")
    
    if not live_df.empty:
        grouped = live_df.groupby("Sector Index")
        for sector_name, sec_df in sorted(grouped):
            with st.expander(f"📁 {sector_name} ({len(sec_df)} Stocks)", expanded=False):
                _, _, sec_tf_df = fetch_day_movers_with_multi_timeframes(sec_df, now_str)
                if not sec_tf_df.empty:
                    styled_sec = sec_tf_df.style.map(
                        style_price_change, subset=["Price Change %"]
                    ).format({"Price Change %": "{:+.2f}%", "End Rel Vol": "{:.2f}"})
                    st.dataframe(styled_sec, column_config=LINK_COLUMN_CONFIG, use_container_width=True)
    else:
        st.info("Loading stock breakdown...")
