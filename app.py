# ==========================================
# SIDEBAR / CUSTOM RANGE GENERATOR
# ==========================================
# Generate 5-minute intervals starting from market open (09:15 AM to 03:30 PM)
def generate_5min_intervals():
    intervals = []
    start = datetime.combine(datetime.today(), time(9, 15))
    end = datetime.combine(datetime.today(), time(15, 30))
    
    current = start
    while current < end:
        next_interval = current + timedelta(minutes=5)
        label = f"{current.strftime('%I:%M %p')} - {next_interval.strftime('%I:%M %p')}"
        intervals.append((label, current.time(), next_interval.time()))
        current = next_interval
    return intervals

five_min_slots = generate_5min_intervals()
slot_labels = [slot[0] for slot in five_min_slots]

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 5-Minute Time Windows")
selected_slot_label = st.sidebar.selectbox(
    "Select 5-Min Market Slot:",
    options=slot_labels,
    index=0
)

# Extract start and end times for selected slot
selected_slot = next(slot for slot in five_min_slots if slot[0] == selected_slot_label)
custom_start_time = selected_slot[1]
custom_end_time = selected_slot[2]

if st.sidebar.button("🧹 Reset Snapshot Database"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relvol_snapshots")
    conn.commit()
    conn.close()
    st.sidebar.success("Database cleared!")
    st.rerun()

# ==========================================
# CUSTOM RANGE TAB
# ==========================================
with tab_custom:
    start_ts_str = f"{today_date_str} {custom_start_time.strftime('%H:%M:%S')}"
    end_ts_str = f"{today_date_str} {custom_end_time.strftime('%H:%M:%S')}"
    
    st.subheader(f"Top Gainers for Slot: {selected_slot_label}")
    
    df_custom, gain_col_name, act_start, act_end = calculate_gain_by_exact_timestamps(
        start_ts_str, 
        end_ts_str, 
        segment_filter=selected_segment, 
        label_name="5m Slot Gain"
    )
    
    if not df_custom.empty:
        st.caption(f"Snapshot delta: `{act_start.split(' ')[1]}` ➔ `{act_end.split(' ')[1]}`.")
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
        st.info(f"No snapshot data recorded for {selected_slot_label} yet. Ensure Streamlit is running during market hours to log snapshots continuously.")
