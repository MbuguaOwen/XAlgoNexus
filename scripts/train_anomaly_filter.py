import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# Paths
input_csv = Path("ml_model/data/features_triangular_labeled.csv")
output_model = Path("ml_model/anomaly_filter.pkl")

# Load data
print("📥 Loading features for anomaly detection...")
df = pd.read_csv(input_csv)

# Drop the label (unsupervised training)
X = df.drop(columns=["label"], errors="ignore")

# Scale features
print("⚙️ Scaling feature data...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest
print("🧠 Training Isolation Forest...")
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(X_scaled)

# Save model and scaler
joblib.dump({"model": model, "scaler": scaler}, output_model)
print(f"✅ Anomaly filter saved to: {output_model}")
