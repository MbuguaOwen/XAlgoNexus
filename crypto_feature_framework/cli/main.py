
import argparse
import pandas as pd
from core.indicators import compute_features

def main():
    parser = argparse.ArgumentParser(description="Crypto Feature Extractor CLI")
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--output', default='features_sample.csv', help='Path to output features CSV')
    parser.add_argument('--interval', default='1min', help='Time interval for resampling')

    args = parser.parse_args()
    df = pd.read_csv(args.input)
    df.columns = [c.lower() for c in df.columns]

    features = compute_features(df, resample_interval=args.interval)
    features.to_csv(args.output)
    print(f"✅ Features written to {args.output}")

if __name__ == "__main__":
    main()
