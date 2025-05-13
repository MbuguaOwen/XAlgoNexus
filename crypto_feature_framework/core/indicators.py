
import numpy as np
import pandas as pd

def compute_vwap(df):
    return (df['price'] * df['quantity']).sum() / df['quantity'].sum()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def compute_bollinger_bands(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (num_std * std)
    lower_band = sma - (num_std * std)
    return sma, upper_band, lower_band

def compute_trade_frequency(df, resample_interval='1min'):
    trade_counts = df.resample(resample_interval).size()
    return trade_counts

def compute_features(df, resample_interval='1min'):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df.sort_index()

    resampled = df.resample(resample_interval).agg({
        'price': 'last',
        'quantity': 'sum'
    }).dropna()

    resampled['vwap'] = df.resample(resample_interval).apply(compute_vwap)
    resampled['sma_14'] = resampled['price'].rolling(window=14).mean()
    resampled['ema_14'] = resampled['price'].ewm(span=14, adjust=False).mean()
    resampled['rsi_14'] = compute_rsi(resampled['price'])
    bb_mid, bb_upper, bb_lower = compute_bollinger_bands(resampled['price'])
    resampled['bb_mid'] = bb_mid
    resampled['bb_upper'] = bb_upper
    resampled['bb_lower'] = bb_lower
    resampled['trade_freq'] = compute_trade_frequency(df, resample_interval=resample_interval)

    return resampled.dropna()
 