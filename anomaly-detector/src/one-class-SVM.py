# Similar to Support Vector Machine (SVM), but for unsupervised anomaly detection. 
# It works by finding a hyperplane that best separates the normal data from the origin in the feature space. 
# The points that are farthest from the hyperplane are considered anomalies.

from sklearn.svm import OneClassSVM
import pandas as pd

# Load training data (normal only)
df_train = pd.read_csv("logs/merged/normal.csv")

features = [
  "water_level", "water_demand",
  "inlet", "outlet", "pump",
  "packet_count", "avg_packet_rate",
  "avg_interval_since_last", "write_count"
]

X_train = df_train[features].astype(float)

# Train model
model = OneClassSVM(kernel="rbf", gamma="scale", nu=0.01)
model.fit(X_train)

# Test on attack data
df_test = pd.read_csv("logs/attacks/packetCount.csv")

X_test = df_test[features].astype(float)

predictions = model.predict(X_test)
df_test["anomaly"] = predictions

anomalies = df_test[df_test["anomaly"] == -1]

print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())

df_test.to_csv("logs/One-Class-SVM/packetCount_with_predictions.csv", index=False)