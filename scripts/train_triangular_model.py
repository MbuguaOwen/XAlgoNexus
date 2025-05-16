import argparse
import yaml
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from scipy.stats import zscore
from binance_downloader import download_binance_klines

# --- Load Config ---
def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# --- Feature Engineering ---
def compute_features(df_btc, df_eth, df_ethbtc, cfg):
    df = pd.concat([df_btc, df_eth, df_ethbtc], axis=1, keys=['btc', 'eth', 'ethbtc'])
    df.columns = ['btc_price', 'btc_vol', 'eth_price', 'eth_vol', 'ethbtc_price', 'ethbtc_vol']

    df['implied_ethbtc'] = df['eth_price'] / df['btc_price']
    df['spread'] = df['implied_ethbtc'] - df['ethbtc_price']
    df['zscore'] = zscore(df['spread'].ffill().dropna(), nan_policy='omit')

    for win in cfg['feature_params']['momentum_windows']:
        df[f'mom_btc_{win}'] = df['btc_price'].pct_change(win)
        df[f'mom_eth_{win}'] = df['eth_price'].pct_change(win)
        df[f'mom_ethbtc_{win}'] = df['ethbtc_price'].pct_change(win)

    df['vol_spread'] = df['spread'].rolling(cfg['feature_params']['vol_window']).std()
    return df.dropna()

# --- Triple-Barrier Labeling ---
def label_triple_barrier(df, horizon, vol_mult):
    labels = np.zeros(len(df))
    rolling_std = df['spread'].rolling(horizon).std()

    for i in range(len(df) - horizon):
        current_spread = df['spread'].iloc[i]
        thresh = vol_mult * rolling_std.iloc[i]
        future = df['spread'].iloc[i+1:i+horizon+1]

        tp = current_spread + thresh
        sl = current_spread - thresh

        if (future >= tp).any():
            labels[i] = 1
        elif (future <= sl).any():
            labels[i] = -1
        else:
            labels[i] = 0

    df = df.iloc[:len(labels)].copy()
    df['label'] = labels
    return df.dropna()

# --- Model Training (Last Fold Only) ---
def walk_forward_train(X, y, cfg):
    print("🧠 Starting model training...")
    tscv = TimeSeriesSplit(n_splits=cfg['train_test_split']['folds'])

    final_model = None
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
        print(f"📦 Fold {fold}: Training...")
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = XGBClassifier(objective='multi:softprob', eval_metric='mlogloss')
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(classification_report(y_test, y_pred))

        final_model = model  # Last model for export

    return final_model

# --- Main Entrypoint ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml_model/config/default_config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    interval = cfg['resample_interval']

    print("📥 Downloading Binance data...")
    df_btc = download_binance_klines("BTCUSDT", interval, "2022-01-01", "2022-12-31")
    df_eth = download_binance_klines("ETHUSDT", interval, "2022-01-01", "2022-12-31")
    df_ethbtc = download_binance_klines("ETHBTC", interval, "2022-01-01", "2022-12-31")

    print("🔧 Performing feature engineering...")
    df = compute_features(df_btc, df_eth, df_ethbtc, cfg)

    print("🏷️ Labeling with triple-barrier method...")
    df = label_triple_barrier(df, cfg['labeling_params']['horizon'], cfg['labeling_params']['volatility_multiplier'])

    print("💾 Saving features for downstream use...")
    df.to_csv("ml_model/data/features_triangular_labeled.csv", index=False)

    print("🎯 Training classifier...")
    X = df.drop(columns=['label'])
    y = df['label'].map({-1: 0, 0: 1, 1: 2})  # XGBoost requires [0,1,2]

    model = walk_forward_train(X, y, cfg)

    print("📦 Saving model as .pkl for confidence scoring...")
    joblib.dump(model, "ml_model/triangular_rf_model.pkl")
    print("✅ Model saved as: ml_model/triangular_rf_model.pkl")

if __name__ == "__main__":
    main()
