import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

@st.cache_data
def _load_raw(symbol):
    path = f'./data/{symbol}_5Years_8_11_2024.csv'
    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['Time']).dt.round('min')
    df['Date'] = df['datetime'].dt.date
    df['Time'] = df['datetime'].dt.time
    df = df.set_index('datetime')
    return df

def get_dataset(symbol):
    if symbol == "ES":
        return st.session_state.es_df
    elif symbol == "NQ":
        return st.session_state.nq_df
    elif symbol == "NQ - ES":
        return st.session_state.nq_df, st.session_state.es_df
    else:
        raise ValueError(f"Unsupported symbol: {symbol}")

def generate_trade_data(dates, time_start, time_end, dataset_choice):
    rows = []

    for date_str in dates:
        date_obj = pd.to_datetime(date_str).date()
        start_dt = pd.Timestamp(datetime.combine(date_obj, time_start)).round('min')
        end_dt = pd.Timestamp(datetime.combine(date_obj, time_end)).round('min')

        if dataset_choice == "NQ - ES":
            nq_df, es_df = get_dataset("NQ - ES")
            if start_dt not in nq_df.index or start_dt not in es_df.index:
                continue
            if end_dt not in nq_df.index or end_dt not in es_df.index:
                continue

            nq_start = nq_df.loc[start_dt]["Close"]
            es_start = es_df.loc[start_dt]["Close"]
            nq_end = nq_df.loc[end_dt]["Close"]
            es_end = es_df.loc[end_dt]["Close"]

            row = {
                "date": date_str,
                "start_dt": start_dt,
                "end_dt": end_dt,
                "NQ_start": nq_start,
                "ES_start": es_start,
                "NQ_end": nq_end,
                "ES_end": es_end,
                "NQ_diff": nq_end - nq_start,
                "ES_diff": es_end - es_start,
                "start_price": nq_start - es_start,
                "end_price": nq_end - es_end,
                "diff": (nq_end - es_end) - (nq_start - es_start),
            }

        else:
            df = get_dataset(dataset_choice)
            if start_dt not in df.index or end_dt not in df.index:
                continue

            start_price = df.loc[start_dt]["Close"]
            end_price = df.loc[end_dt]["Close"]

            row = {
                "date": date_str,
                "start_dt": start_dt,
                "end_dt": end_dt,
                "start_price": start_price,
                "end_price": end_price,
                "diff": end_price - start_price,
            }

        rows.append(row)

    return pd.DataFrame(rows)

def backtest(trade_df, position='long'):
    if position == 'long':
        trade_df['PnL'] = trade_df['diff']
    elif position == 'short':
        trade_df['PnL'] = -trade_df['diff']
    else:
        raise ValueError("Position must be 'long' or 'short'")

    trade_df['cumulative_PnL'] = trade_df['PnL'].cumsum()
    return trade_df

def calculate_annualized_sharpe(trade_df):
    num_trades = len(trade_df)
    mean_pnl = trade_df['PnL'].mean()
    std_pnl = trade_df['PnL'].std(ddof=0)

    if num_trades < 2 or std_pnl == 0:
        return np.nan, mean_pnl, std_pnl, num_trades, None

    dates = pd.to_datetime(trade_df['date']).sort_values()
    gaps = dates.diff().dt.days.dropna()
    avg_gap = gaps.mean() or 1

    sharpe = (mean_pnl / std_pnl) * np.sqrt(252 / avg_gap)
    return sharpe, mean_pnl, std_pnl, num_trades, avg_gap

def display_backtest_results(bt_result, dataset_choice):
    sharpe, mean_pnl, std_pnl, num_days, avg_gap = calculate_annualized_sharpe(bt_result)

    fig = px.line(bt_result, x='date', y='cumulative_PnL', title=f'{dataset_choice} Cumulative PnL')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Annualized Sharpe Ratio:** {sharpe:.3f}")
    st.markdown(f"- Mean PnL: {mean_pnl:.4f}")
    st.markdown(f"- Std PnL: {std_pnl:.4f}")
    st.markdown(f"- Number of Trades: {num_days}")
    st.markdown(f"- Avg Days Between Trades: {avg_gap:.2f}")

    st.dataframe(bt_result, use_container_width=True)