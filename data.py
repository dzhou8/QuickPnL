import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

@st.cache_data
def load_data(symbol):
    if symbol == "ES":
        path = './data/ES_5Years_8_11_2024.csv'
    elif symbol == "NQ":
        path = './data/NQ_5Years_8_11_2024.csv'
    else:
        raise ValueError("Unsupported symbol")

    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['Time']).dt.round('min')
    df['Date'] = df['datetime'].dt.date
    df['Time'] = df['datetime'].dt.time
    df = df.set_index('datetime')
    return df

def generate_trade_data(df, dates, time_start, time_end):
    rows = []
    for date_str in dates:
        date_obj = pd.to_datetime(date_str).date()
        start_dt = pd.Timestamp(datetime.combine(date_obj, time_start)).round('min')
        end_dt = pd.Timestamp(datetime.combine(date_obj, time_end)).round('min')

        if start_dt in df.index and end_dt in df.index:
            start_price = df.loc[start_dt]['Close']
            end_price = df.loc[end_dt]['Close']
            diff = end_price - start_price

            rows.append({
                'date': date_str,
                'start_dt': start_dt,
                'end_dt': end_dt,
                'start_price': start_price,
                'end_price': end_price,
                'diff': diff
            })

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