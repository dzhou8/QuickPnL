import streamlit as st
import pandas as pd
from datetime import time
from data import (
    _load_raw,  # only used once up front
    generate_trade_data,
    backtest,
    display_backtest_results,
    get_dataset
)
from dates import (
    get_all_filter_checkboxes,
    compute_filtered_dates,
    get_all_event_dates
)

st.set_page_config(layout="wide")
st.title("Simple Backtest Viewer")

# --- Preload datasets once and store in session state ---
if "es_df" not in st.session_state:
    st.session_state.es_df = _load_raw("ES")
if "nq_df" not in st.session_state:
    st.session_state.nq_df = _load_raw("NQ")

# --- Sidebar UI ---
with st.sidebar:
    st.header("Backtest Parameters")

    dataset_choice = st.selectbox("Dataset", ["ES", "NQ", "NQ - ES"])

    valid_time_strs = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in range(0, 60, 5)]
    time_start_str = st.selectbox("Start Time (Eastern)", valid_time_strs, index=valid_time_strs.index("09:30"))
    time_end_str = st.selectbox("End Time (Eastern)", valid_time_strs, index=valid_time_strs.index("16:00"))
    time_start = pd.to_datetime(time_start_str).time()
    time_end = pd.to_datetime(time_end_str).time()

    position = st.selectbox("Position", ['long', 'short'])

    st.subheader("Date Filters")
    selected_filters = get_all_filter_checkboxes()

    # Get all available dates from dataset(s)
    if dataset_choice == "NQ - ES":
        es_dates = set(st.session_state.es_df['Date'].unique())
        nq_dates = set(st.session_state.nq_df['Date'].unique())
        data_dates = sorted(es_dates & nq_dates)
    else:
        df = get_dataset(dataset_choice)
        data_dates = sorted(df['Date'].unique())

    event_dates = set(pd.Series(pd.to_datetime(get_all_event_dates())).dt.date)
    all_available_dates = sorted(set(data_dates).union(event_dates))
    default_dates = compute_filtered_dates(all_available_dates, selected_filters)
    valid_default_dates = sorted(set(default_dates) & set(all_available_dates))

    st.write(f"Selected {len(valid_default_dates)} dates.")
    with st.expander("Edit Selected Dates"):
        dates = st.multiselect("Select Dates", all_available_dates, default=valid_default_dates)

    run = st.button("Run Backtest")

# --- Main content ---
if run:
    if time_end <= time_start:
        st.error("End time must be later than start time.")
    elif not dates:
        st.warning("No dates selected.")
    else:
        trade_df = generate_trade_data(dates, time_start, time_end, dataset_choice)

        if trade_df.empty:
            st.warning("No matching rows found for the selected dates/times.")
        else:
            bt_result = backtest(trade_df, position)
            display_backtest_results(bt_result, dataset_choice)
else:
    st.info("Select parameters on the left and click 'Run Backtest' to begin.")