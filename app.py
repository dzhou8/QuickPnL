# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import time
from data import load_data, generate_trade_data, backtest, calculate_annualized_sharpe
from dates import filter_dates_by_weekday

st.set_page_config(layout="wide")

# --- Title ---
st.title("Simple Backtest Viewer")

# --- Load both datasets ---
ES_df = load_data("ES")
NQ_df = load_data("NQ")

# --- Sidebar ---
with st.sidebar:
    st.header("Backtest Parameters")

    # Dataset selection
    dataset_choice = st.selectbox("Dataset", ["ES", "NQ"])
    df = ES_df if dataset_choice == "ES" else NQ_df

    # Time selection
    valid_times = sorted(df['Time'].unique())
    valid_time_strs = [t.strftime('%H:%M') for t in valid_times]
    time_start_str = st.selectbox("Start Time (Eastern)", valid_time_strs, index=valid_time_strs.index('09:30'))
    time_end_str = st.selectbox("End Time (Eastern)", valid_time_strs, index=valid_time_strs.index('16:00'))
    time_start = pd.to_datetime(time_start_str).time()
    time_end = pd.to_datetime(time_end_str).time()

    # Position type
    position = st.selectbox("Position", ['long', 'short'])

    # Date filtering options
    st.subheader("Date Filtering")
    all_dates = sorted(df['Date'].unique())
    use_all = st.checkbox("Daily")
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_weekdays = [day for day in weekdays if st.checkbox(day)]

    if use_all:
        default_dates = all_dates
    elif selected_weekdays:
        default_dates = filter_dates_by_weekday(all_dates, selected_weekdays)
    else:
        default_dates = []

    st.write(f"Selected {len(default_dates)} dates.")

    with st.expander("Optional: Manually edit selected dates"):
        dates = st.multiselect("Select Dates", all_dates, default=default_dates)

    run = st.button("Run Backtest")

# --- Main panel ---
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