import pandas as pd
from sklearn.ensemble import IsolationForest

df_train = pd.read_csv("logs/merged/normal/normal.csv")

features = [
  "water_level", "water_demand",
  "inlet", "outlet", "pump",
  "packet_count", "avg_packet_rate",
  "avg_interval_since_last", "write_count"
]

X = df_train[features].astype(float)

model = IsolationForest(contamination=0.01, random_state=42)
model.fit(X)

df_test = pd.read_csv("logs/attacks/replay.csv")
# df_test = df_test.iloc[60:].copy()

X_test = df_test[features].astype(float)
predictions = model.predict(X_test)
df_test["anomaly"] = predictions


anomalies = df_test[df_test["anomaly"] == -1]
print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())
df_test.to_csv("logs/isolationForest/replay_with_predictions.csv", index=False)
