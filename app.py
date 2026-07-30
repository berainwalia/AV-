# ==========================================
# SIDEBAR / CUSTOM RANGE GENERATOR
# ==========================================
def generate_5min_intervals():
    intervals = []
    # Use today's date from now_dt or current date
    today_date = now_dt.date()
    
    start = datetime.combine(today_date, time(9, 15))
    end = datetime.combine(today_date, time(15, 30))
    
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
