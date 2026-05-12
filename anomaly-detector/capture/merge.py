###
# Run this script to merge PLC and Network logs.
# Run after completing captures and generating logs with run_captures.py.
###

import pandas as pd
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

plc = pd.read_csv(BASE / "logs/plc/normal/plc_data_log.csv")
plc = plc.drop(columns=["experiment"])

network = pd.read_csv(BASE / "logs/network/normal/network_log.csv")

plc["timestamp"] = pd.to_datetime(plc["timestamp"], format="ISO8601")
network["timestamp"] = pd.to_datetime(network["timestamp"], format="ISO8601")

network = network.iloc[100:]

network = network.dropna(subset=["interval_since_last"])
network = network[network["interval_since_last"] > 0.001]

network = network[network["packet_rate"] < 1000]

start_time = network["timestamp"].min()
plc = plc[plc["timestamp"] >= start_time]

plc = plc.sort_values("timestamp").reset_index(drop=True)
network = network.sort_values("timestamp").reset_index(drop=True)

network["is_write"] = network["function_code"].isin([5, 6, 15, 16]).astype(int)

network = network.set_index("timestamp")
plc = plc.set_index("timestamp")

aggregation = network.resample("100ms").agg({
  "function_code": "count",
  "interval_since_last": "mean",
  "is_write": "sum"
})

aggregation.columns = [
  "packet_count",
  "avg_interval_since_last",
  "write_count"
]

aggregation = aggregation.fillna(0)

merged = pd.merge_asof(
  plc.sort_index(),
  aggregation.sort_index(),
  left_index=True,
  right_index=True,
  direction="backward",
  tolerance=pd.Timedelta("100ms")
).fillna(0)

combined = merged.reset_index()

os.makedirs(BASE / "logs/merged", exist_ok=True)
combined.to_csv(BASE / "logs/merged/merged_log.csv", index=False)

print("Combined dataset saved to /logs/merged/merged_log.csv")
