import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import time
from data import (
    load_data,
    generate_trade_data,
    backtest,
    calculate_annualized_sharpe,
)
from dates import (
    get_all_filter_checkboxes,
    compute_filtered_dates,
    get_all_event_dates
)

st.set_page_config(layout="wide")
st.title("Simple Backtest Viewer")

# --- Load datasets ---
ES_df = load_data("ES")
NQ_df = load_data("NQ")

# --- Sidebar UI ---
with st.sidebar:
    st.header("Backtest Parameters")

    dataset_choice = st.selectbox("Dataset", ["ES", "NQ"])
    df = ES_df if dataset_choice == "ES" else NQ_df

    # Show dataset date range
    st.markdown(f"**Date Range Loaded:** {df['Date'].min()} → {df['Date'].max()}")

    valid_times = sorted(df['Time'].unique())
    valid_time_strs = [t.strftime('%H:%M') for t in valid_times]
    time_start_str = st.selectbox("Start Time (Eastern)", valid_time_strs, index=valid_time_strs.index('09:30'))
    time_end_str = st.selectbox("End Time (Eastern)", valid_time_strs, index=valid_time_strs.index('16:00'))
    time_start = pd.to_datetime(time_start_str).time()
    time_end = pd.to_datetime(time_end_str).time()

    position = st.selectbox("Position", ['long', 'short'])

    # Filter checkboxes
    st.subheader("Date Filters")
    selected_filters = get_all_filter_checkboxes()

    # Combine dates from dataset and event files
    df_dates = set(df['Date'].unique())
    event_dates = set(pd.Series(pd.to_datetime(get_all_event_dates())).dt.date)
    all_dates = sorted(df_dates.union(event_dates))

    # Get final list of dates from selected filters
    default_dates = compute_filtered_dates(all_dates, selected_filters)
    valid_default_dates = [d for d in default_dates if d in all_dates]

    st.write(f"Selected {len(valid_default_dates)} dates.")
    with st.expander("Edit Selected Dates"):
        dates = st.multiselect("Select Dates", all_dates, default=valid_default_dates)

    run = st.button("Run Backtest")

# --- Main content ---
if run:
    if time_end <= time_start:
        st.error("End time must be later than start time.")
    else:
        trade_df = generate_trade_data(df, dates, time_start, time_end)

        if trade_df.empty:
            st.warning("No matching rows found for the selected dates/times.")
        else:
            bt_result = backtest(trade_df, position)
            sharpe, mean_pnl, std_pnl, num_days, avg_gap = calculate_annualized_sharpe(bt_result)

            fig = px.line(bt_result, x='date', y='cumulative_PnL', title=f'{dataset_choice} Cumulative PnL')
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**Annualized Sharpe Ratio:** {sharpe:.3f}")
            st.markdown(f"- Mean PnL: {mean_pnl:.4f}")
            st.markdown(f"- Std PnL: {std_pnl:.4f}")
            st.markdown(f"- Number of Trades: {num_days}")
            st.markdown(f"- Avg Days Between Trades: {avg_gap:.2f}")

            st.dataframe(bt_result, use_container_width=True)
else:
    st.info("Select parameters on the left and click 'Run Backtest' to begin.")