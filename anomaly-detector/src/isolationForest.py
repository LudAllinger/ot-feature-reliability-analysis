import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

df_train = pd.read_csv("logs/merged/normal.csv")

features = [
  "water_level", "water_demand",
  "inlet", "outlet", "pump",
  "packet_count", "avg_packet_rate",
  "avg_interval_since_last", "write_count"
]

X = df_train[features].astype(float)

model = IsolationForest(random_state=42)
model.fit(X)

df = pd.read_csv("logs/attacks/DoS.csv")
X_test = df[features].astype(float)

scores = model.decision_function(X_test)
df["score"] = scores

threshold = np.percentile(scores, 1)

df["anomaly"] = (scores < threshold).astype(int)
df["anomaly"] = df["anomaly"].apply(lambda x: -1 if x == 1 else 1)

anomalies = df[df["anomaly"] == -1]

print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())

df.to_csv("logs/isolationForest/DoS_with_predictions.csv", index=False)