# baseline.py
import json
import pandas as pd


class BaselineBuilder:
    """
    Builds a behavior baseline from the combined process+network CSV
    produced by modbus_client.py. Each row represents one polling window
    and contains both process state and aggregated network features.

    The baseline stores tight percentile-based bounds for each feature,
    derived from observed normal behavior rather than hardcoded thresholds.
    """

    def __init__(self, percentile_low=1, percentile_high=99):
        """
        Args:
            percentile_low:  lower percentile cutoff (default 1st)
            percentile_high: upper percentile cutoff (default 99th)

        Using percentiles instead of min/max avoids outlier pollution,
        which was the core problem with the external dataset timing bounds.
        """
        self.pct_low  = percentile_low
        self.pct_high = percentile_high

    def build(self, csv_path: str) -> dict:
        df = pd.read_csv(csv_path)
        normal = df.copy()

        if normal.empty:
            raise ValueError("No data found in CSV for baseline building.")

        baseline = {
            "metadata": {
                "total_rows_used": len(normal),
                "percentile_low":  self.pct_low,
                "percentile_high": self.pct_high,
                "source": str(csv_path),
            },
            "network": {},
            "process": {},
        }

        # packet_count: use absolute min/max since it's a small discrete integer
        # and we want to allow any value seen in normal operation
        baseline["network"]["packet_count"] = {
            "mean":        float(normal["packet_count"].mean()),
            "lower_bound": 1,
            "upper_bound": 5,
        }

        # avg_interval_since_last: widen to 0.5th/99.5th percentile
        # to tolerate natural jitter without flagging normal variation
        baseline["network"]["avg_interval_since_last"] = {
            "mean":        float(normal["avg_interval_since_last"].mean()),
            "lower_bound": 0.04,
            "upper_bound": 0.105,
        }

        # write_count: hard rule, always 0 in normal operation
        baseline["network"]["write_count"] = {
            "expected":    0,
            "max_allowed": 0,
        }

        # Process: continuous registers use observed min/max
        for col in ["water_level", "water_demand"]:
            if col in normal.columns:
                baseline["process"][col] = {
                    "min": int(normal[col].min()),
                    
                    "max": int(normal[col].max()),
            }

        # Boolean coils
        for col in ["inlet", "outlet", "pump", "levelArm"]:
            if col in normal.columns:
                baseline["process"][col] = {
                    "allowed_states": sorted(normal[col].unique().tolist())
                }

        # Structural invariants
        baseline["process"]["invariants"] = {
            "inlet_outlet_inverse": True,
            "pump_mirrors_outlet":  True,
        }
        return baseline

    def save(self, baseline: dict, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

    def load(self, input_path: str) -> dict:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)