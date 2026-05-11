import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

BASE = Path(__file__).resolve().parent.parent

df_train = pd.read_csv(BASE / "logs" / "merged" / "normal.csv")

features = [
  "water_level", "water_demand",
  "inlet", "outlet", "pump",
  "packet_count", "avg_packet_rate",
  "avg_interval_since_last", "write_count"
]

X = df_train[features].astype(float)

model = IsolationForest(random_state=42)
model.fit(X)

ATTACK_FILE = BASE / "logs" / "attacks" / "packetCount.csv"
OUTPUT_FILE = BASE / "logs" / "isolationForest" / f"{ATTACK_FILE.stem}_with_predictions.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ATTACK_FILE)
X_test = df[features].astype(float)

scores = model.decision_function(X_test)
df["score"] = scores

threshold = np.percentile(scores, 1)

df["anomaly"] = (scores < threshold).astype(int)
df["anomaly"] = df["anomaly"].apply(lambda x: -1 if x == 1 else 1)

anomalies = df[df["anomaly"] == -1]

print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())


df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved to: {OUTPUT_FILE}")