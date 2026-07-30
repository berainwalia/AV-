import streamlit as st
import pandas as pd
from tradingview_screener import Query, col

# Set up page config
st.set_page_config(page_title="Stock Screener & Custom Stocks", layout="wide")

# Initialize session state for custom stock list if not already present
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = ["NSE:TATAMOTORS", "NSE:SBIN", "NSE:RELIANCE"]

def fetch_custom_stock_data(symbols):
    """
    Fetches real-time market results and sector info for a list of ticker symbols from TradingView.
    """
    if not symbols:
        return pd.DataFrame()
    
    # Normalize tickers (ensure NSE: prefix if missing)
    clean_symbols = []
    for s in symbols:
        s = s.strip().upper()
        if not s.startswith("NSE:") and not ":" in s:
            s = f"NSE:{s}"
        clean_symbols.append(s)
    
    # Extract raw stock names for filtering (e.g., 'TATAMOTORS' from 'NSE:TATAMOTORS')
    raw_names = [s.split(":")[-1] for s in clean_symbols]

    try:
        # Query TradingView Screener API
        q = (
            Query()
            .set_markets("india")
            .select(
                "name",
                "sector",
                "close",
                "change",
                "volume",
                "relative_volume_10d_calc",
                "RSI",
                "MACD.macd",
                "MACD.signal"
            )
            .where(col("name").isin(raw_names)) # Filter by user's stock list
        )
        _, df = q.get_scanner_data()
        
        if not df.empty:
            # Rename columns for cleaner display
            df = df.rename(
                columns={
                    "ticker": "Ticker",
                    "name": "Symbol",
                    "sector": "Sector",
                    "close": "Price (₹)",
                    "change": "Change (%)",
                    "volume": "Volume",
                    "relative_volume_10d_calc": "Rel Vol (10d)",
                    "RSI": "RSI (14)",
                }
            )
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching data from TradingView: {e}")
        return pd.DataFrame()


# Create Main Tabs
tab1, tab2 = st.tabs(["📊 Main Screener", "➕ Add Custom / Missing F&O Stocks"])

# ---------------------------------------------------------
# TAB 1: MAIN SCREENER
# ---------------------------------------------------------
with tab1:
    st.header("Automated F&O Screener")
    st.write("Displays auto-screened F&O stocks...")
    # Your existing screener logic goes here


# ---------------------------------------------------------
# TAB 2: MANUAL / CUSTOM STOCKS
# ---------------------------------------------------------
with tab2:
    st.header("Manual Stock Insertion & Auto-Sector Resolution")
    st.markdown(
        "Enter any missing F&O stock symbol. TradingView will automatically fetch "
        "its live price, technical indicators, and sector."
    )

    col_input, col_btn = st.columns([3, 1])

    with col_input:
        new_ticker_input = st.text_input(
            "Add Stock Symbol(s)",
            placeholder="e.g. INFOSYS, NSE:HDFCBANK, TCS (separate multiple with commas)",
            key="new_ticker_input"
        )

    with col_btn:
        st.write(" ") # Alignment spacer
        if st.button("➕ Add Stock(s)", use_container_width=True):
            if new_ticker_input:
                # Parse multiple comma-separated inputs
                input_list = [s.strip().upper() for s in new_ticker_input.split(",") if s.strip()]
                
                # Format to NSE prefix standard
                formatted_list = [s if ":" in s else f"NSE:{s}" for s in input_list]
                
                # Append non-duplicates to session state
                added_count = 0
                for item in formatted_list:
                    if item not in st.session_state.custom_tickers:
                        st.session_state.custom_tickers.append(item)
                        added_count += 1
                
                if added_count > 0:
                    st.success(f"Added {added_count} stock(s) to custom watchlist!")
                else:
                    st.info("Stock(s) already in watchlist.")
            else:
                st.warning("Please enter at least one stock symbol.")

    st.divider()

    # Display Managed Watchlist
    st.subheader("Your Custom Stock Watchlist")

    if st.session_state.custom_tickers:
        # Fetch fresh data for custom tickers
        with st.spinner("Fetching live stock results & sector details..."):
            custom_df = fetch_custom_stock_data(st.session_state.custom_tickers)

        if not custom_df.empty:
            # Display interactive dataframe
            st.dataframe(
                custom_df,
                use_container_width=True,
                column_config={
                    "Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Change (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "Volume": st.column_config.NumberColumn(format="%d"),
                    "Rel Vol (10d)": st.column_config.NumberColumn(format="%.2fx"),
                    "RSI (14)": st.column_config.NumberColumn(format="%.2f"),
                },
                hide_index=True
            )
        else:
            st.warning("No data found for specified tickers. Please verify stock symbols.")

        # Sidebar or expander option to clear custom tickers
        with st.expander("Manage List"):
            st.write("Current Tickers in Watchlist:", st.session_state.custom_tickers)
            if st.button("🗑️ Clear All Custom Stocks"):
                st.session_state.custom_tickers = []
                st.rerun()
    else:
        st.info("No custom stocks added yet. Use the input field above to add some!")
