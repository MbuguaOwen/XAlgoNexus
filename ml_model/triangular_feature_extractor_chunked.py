
import pandas as pd

def process_chunk(chunk, label):
    chunk.columns = [
    "trade_id", "price", "quantity", "quote_quantity",
    "timestamp", "buyer_is_maker", "best_match"
]
    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], unit="ms", errors='coerce')
    chunk = chunk.dropna(subset=["timestamp"])
    return chunk.set_index("timestamp").resample("1min").agg({"price": "mean"}).rename(columns={"price": label})

def load_large_file_in_chunks(path, label, chunksize=1_000_000):
    all_chunks = []
    for chunk in pd.read_csv(path, chunksize=chunksize):
        resampled = process_chunk(chunk, label)
        all_chunks.append(resampled)
    return pd.concat(all_chunks).sort_index()

def compute_features_large(btc_path, ethusd_path, ethbtc_path, output_path):
    print("🔄 Processing BTCUSD...")
    btc_df = load_large_file_in_chunks(btc_path, "btc_usd")

    print("🔄 Processing ETHUSD...")
    ethusd_df = load_large_file_in_chunks(ethusd_path, "eth_usd")

    print("🔄 Processing ETHBTC...")
    ethbtc_df = load_large_file_in_chunks(ethbtc_path, "eth_btc")

    # Merge and compute features
    df = btc_df.join(ethusd_df).join(ethbtc_df).dropna()
    df["implied_ethbtc"] = df["eth_usd"] / df["btc_usd"]
    df["spread"] = df["eth_btc"] - df["implied_ethbtc"]
    df["z_score"] = (df["spread"] - df["spread"].rolling(30).mean()) / df["spread"].rolling(30).std()

    df.dropna().reset_index().to_csv(output_path, index=False)
    print(f"✅ Feature file saved to {output_path}")

if __name__ == "__main__":
    compute_features_large(
        btc_path="ml_model/BTCUSD.csv",
        ethusd_path="ml_model/ETHUSD.csv",
        ethbtc_path="ml_model/ETHBTC.csv",
        output_path="ml_model/features_triangular_full.csv"
    )
