import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent.parent

df_train = pd.read_csv(BASE / "logs" / "merged" / "normal.csv")

features = [
  "water_level", "water_demand",
  "inlet", "outlet", "pump",
  "packet_count","avg_interval_since_last", "write_count"
]

X_train = df_train[features].astype(float)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = IsolationForest(random_state=42)
model.fit(X_train_scaled)

ATTACK_FILE = BASE / "logs" / "attacks" / "waterLevel.csv"
".csv"
OUTPUT_FILE = BASE / "logs" / "isolationForest" / f"{ATTACK_FILE.stem}_with_predictions.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df_test = pd.read_csv(ATTACK_FILE)
X_test = df_test[features].astype(float)
X_test_scaled = scaler.transform(X_test)

scores = model.decision_function(X_test_scaled)
df_test["score"] = scores

train_scores = model.decision_function(X_train_scaled)
threshold = np.percentile(train_scores, 1)

df_test["anomaly"] = np.where(scores < threshold, -1, 1).astype(int)

anomalies = df_test[df_test["anomaly"] == -1]

total_rows = len(df_test)
total_anomalies = len(anomalies)

detection_rate = (total_anomalies / total_rows) * 100
print(f"Total rows: {total_rows}")
print(f"Detection rate: {detection_rate:.2f}%")

print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())

df_test.to_csv(OUTPUT_FILE, index=False)
print(f"Saved to: {OUTPUT_FILE}")