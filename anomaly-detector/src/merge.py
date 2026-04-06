###
# Run this script to merge PLC and Network logs.
# Run after completing captures and generating logs with run_captures.py.
###

import pandas as pd
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

plc = pd.read_csv(BASE / "logs/plc/normal/plc_data_log.csv")
network = pd.read_csv(BASE / "logs/network/normal/network_log.csv")

plc["timestamp"] = pd.to_datetime(plc["timestamp"])
network["timestamp"] = pd.to_datetime(network["timestamp"])

network["interval_since_last"] = network["interval_since_last"].fillna(0)

plc = plc.sort_values("timestamp").reset_index(drop=True)
network = network.sort_values("timestamp").reset_index(drop=True)
network["is_write"] = network["function_code"].isin([5, 6, 15, 16]).astype(int)

merged = pd.merge_asof(
  plc, 
  network, 
  on="timestamp", 
  direction="nearest", 
  tolerance=pd.Timedelta("100ms"), 
  suffixes=("_plc", "_network")
  )

os.makedirs(BASE / "logs/merged/normal", exist_ok=True)

merged.to_csv(BASE / "logs/merged/normal/merged_log.csv", index=False)

print("Merged dataset saved to /logs/merged/normal/merged_log.csv")

network = network.set_index("timestamp")
plc = plc.set_index("timestamp")

aggregation = network.resample("100ms").agg({
  "function_code": "count",
  "packet_rate": "mean",
  "interval_since_last": "mean",
  "is_write": "sum"
})

aggregation.columns = ["packet_count", "avg_packet_rate", "avg_interval_since_last", "write_count"]

combine = pd.merge_asof(
    plc.sort_index(),
    aggregation.sort_index(),
    left_index=True,
    right_index=True,
    direction="nearest",
    tolerance=pd.Timedelta("100ms")
).fillna(0)

combine = combine.reset_index()

combine.to_csv(BASE / "logs/merged/normal/combined_log.csv", index=False)
print("Combined dataset saved to /logs/merged/normal/combined_log.csv")
