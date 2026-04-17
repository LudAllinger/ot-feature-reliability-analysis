# test_normal.py
import pandas as pd
from anomalyDetector import AnomalyDetector, ALL_RULES, NETWORK_RULES, PROCESS_RULES

BASELINE = r"C:\Users\ameli\OneDrive\Documents\thesis\thesis\anomaly-detector\src\baseline.json"
NORMAL   = r"C:\Users\ameli\OneDrive\Documents\thesis\thesis\anomaly-detector\src\normalAltered.csv"

detector = AnomalyDetector.from_file(BASELINE)
df       = pd.read_csv(NORMAL)
rows     = df.to_dict(orient="records")

all_alerts = []
for row in rows:
    all_alerts.extend(detector.check(row))

print(f"Total rows:   {len(rows)}")
print(f"Total alerts: {len(all_alerts)}")
print(f"False positive rate: {len(all_alerts)/len(rows)*100:.2f}%")

if all_alerts:
    print("\nSample false positives (first 150):")
    for a in all_alerts[:150]:
        print(f"  [{a['rule']}] {a['detail']} @ {a['timestamp']}")