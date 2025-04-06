# QuickPnL

**QuickPnL** is a simple, fast tool for backtesting futures trading ideas.
Try the live demo → [quickpnl.streamlit.app](https://quickpnl.streamlit.app/)

## What is QuickPnL?

QuickPnL helps you quickly evaluate how trading strategies would have performed on **S&P 500 (ES)**, **Nasdaq (NQ)**, or the **NQ - ES spread** over the past 5 years — no code required.

With just a few clicks, you can:
- Filter for specific macro dates (e.g., CPI, NFP, monthly expiry)
- Select intraday windows (e.g., 9:30 to 10:00 AM EST)
- Choose long or short positions
- Instantly see performance metrics: Sharpe ratio, cumulative PnL, and more

It’s a tool designed for rapid iteration — ideal for validating directional or relative value hypotheses with real historical data.

## Demo: Testing a Hypothesis

Let’s say you have a real-world idea you want to test:

> "When Fed Chair Jerome Powell begins speaking at FOMC press conferences, the market reacts with optimism and tends to tick up."

With QuickPnL, you can:

- Select only FOMC days using a preloaded event filter
- Choose a start time of 2:30 PM ET, when Powell typically begins speaking
- Backtest a simple 15-minute long position, capturing the initial market reaction
- Instantly see the historical Sharpe ratio and cumulative PnL

Here’s what that might look like in action:
