# /src/tools/analyze_trade_log.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_trades(path="logs/trade_log.csv"):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp")

    # Simulate trade return = (expected spread * direction)
    # We assume direction: BUY = +spread, SELL = -spread
    df["side_factor"] = df["side"].map({"BUY": 1, "SELL": -1})
    df["trade_return"] = df["spread"] * df["side_factor"]

    # Cumulative return
    df["cum_return"] = df["trade_return"].cumsum()

    return df

def compute_sharpe(trade_returns, risk_free_rate=0.0):
    if len(trade_returns) < 2:
        return 0.0
    excess_returns = trade_returns - risk_free_rate
    return np.mean(excess_returns) / (np.std(excess_returns) + 1e-9) * np.sqrt(252)

def analyze():
    df = load_trades()

    print(f"Total Trades: {len(df)}")
    print(f"Cumulative Return: {df['cum_return'].iloc[-1]:.4f}")
    sharpe = compute_sharpe(df['trade_return'])
    print(f"Sharpe Ratio: {sharpe:.2f}")

    # Optional Plot
    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["cum_return"], label="Equity Curve")
    plt.title("Simulated PnL Curve")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Return")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("logs/equity_curve.png")
    plt.show()

if __name__ == "__main__":
    analyze()
