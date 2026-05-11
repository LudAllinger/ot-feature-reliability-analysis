# anomaly_detector.py
import json
from typing import Optional


RULE_PACKET_COUNT   = "PACKET_COUNT_ANOMALY"
RULE_INTERVAL       = "INTERVAL_ANOMALY"
RULE_WRITE          = "UNEXPECTED_WRITE"
RULE_WATER_LEVEL    = "WATER_LEVEL_ANOMALY"
RULE_WATER_DEMAND   = "WATER_DEMAND_ANOMALY"
RULE_VALVE_STATE    = "VALVE_STATE_ANOMALY"
RULE_PUMP_STATE     = "PUMP_STATE_ANOMALY"

ALL_RULES = {
    RULE_PACKET_COUNT,
    RULE_INTERVAL,
    RULE_WRITE,
    RULE_WATER_LEVEL,
    RULE_WATER_DEMAND,
    RULE_VALVE_STATE,
    RULE_PUMP_STATE,
}

# Groups for per-parameter evaluation
NETWORK_RULES = {RULE_PACKET_COUNT, RULE_INTERVAL, RULE_WRITE}
PROCESS_RULES = {RULE_WATER_LEVEL, RULE_WATER_DEMAND, RULE_VALVE_STATE, RULE_PUMP_STATE}


class AnomalyDetector:
    """
    Rule-based anomaly detector for combined process+network CSV rows.

    Each row represents one polling window (100ms) and contains both
    process state (water level, valves, pump, alarms) and aggregated
    network features (packet count, rate, interval, write count).

    Rules are derived from an empirically observed baseline, not hardcoded
    by a domain expert. Each rule can be enabled or disabled independently
    to support per-parameter evaluation.
    """

    def __init__(self, baseline: dict, enabled_rules: set = None):
        """
        Args:
            baseline:      baseline dict produced by BaselineBuilder
            enabled_rules: set of rule name strings to enable.
                           Pass a single-element set to test one rule at a time.
                           Defaults to ALL_RULES if None.
        """
        self.network  = baseline["network"]
        self.process  = baseline["process"]
        self.enabled  = enabled_rules if enabled_rules is not None else ALL_RULES

    def check(self, row: dict) -> list[dict]:
        """
        Check a single CSV row against the baseline.

        Args:
            row: dict representing one polling window

        Returns:
            list of alert dicts (empty if no anomalies detected)
        """
        alerts = []

        # ── Network rules ────────────────────────────────────────────

        if RULE_PACKET_COUNT in self.enabled:
            v  = row.get("packet_count")
            lo = self.network["packet_count"]["lower_bound"]
            hi = self.network["packet_count"]["upper_bound"]
            if v is not None and not (lo <= v <= hi):
                alerts.append(self._alert(
                    RULE_PACKET_COUNT,
                    f"packet_count={v} outside normal range [{lo:.2f}, {hi:.2f}]",
                    row,
                ))

        if RULE_INTERVAL in self.enabled:
          v  = row.get("avg_interval_since_last")
          lo = self.network["avg_interval_since_last"]["lower_bound"]
          hi = self.network["avg_interval_since_last"]["upper_bound"]
          # skip zero intervals — first packet in a flow has no previous timestamp
          if v is not None and v > 0.001 and not (lo <= v <= hi):
              alerts.append(self._alert(
                  RULE_INTERVAL,
                  f"avg_interval={v:.6f}s outside normal range [{lo:.6f}, {hi:.6f}]",
                  row,
              ))

        if RULE_WRITE in self.enabled:
            v = row.get("write_count", 0)
            if v > self.network["write_count"]["max_allowed"]:
                alerts.append(self._alert(
                    RULE_WRITE,
                    f"write_count={v} — writes never occur in normal operation",
                    row,
                ))

        # ── Process rules ────────────────────────────────────────────

        if RULE_WATER_LEVEL in self.enabled:
            v  = row.get("water_level")
            lo = self.process["water_level"]["min"]
            hi = self.process["water_level"]["max"]
            if v is not None and not (lo <= v <= hi):
                alerts.append(self._alert(
                    RULE_WATER_LEVEL,
                    f"water_level={v} outside normal range [{lo}, {hi}]",
                    row,
                ))

        if RULE_WATER_DEMAND in self.enabled:
            v  = row.get("water_demand")
            lo = self.process["water_demand"]["min"]
            hi = self.process["water_demand"]["max"]
            if v is not None and not (lo <= v <= hi):
                alerts.append(self._alert(
                    RULE_WATER_DEMAND,
                    f"water_demand={v} outside normal range [{lo}, {hi}]",
                    row,
                ))

        if RULE_VALVE_STATE in self.enabled:
            inlet  = row.get("inlet")
            outlet = row.get("outlet")
            if inlet is not None and outlet is not None:
                if self.process["invariants"]["inlet_outlet_inverse"]:
                    if inlet == outlet:
                        alerts.append(self._alert(
                            RULE_VALVE_STATE,
                            f"inlet={inlet} and outlet={outlet} — should always be inverse",
                            row,
                        ))

        if RULE_PUMP_STATE in self.enabled:
            outlet = row.get("outlet")
            pump   = row.get("pump")
            if outlet is not None and pump is not None:
                if self.process["invariants"]["pump_mirrors_outlet"]:
                    if outlet != pump:
                        alerts.append(self._alert(
                            RULE_PUMP_STATE,
                            f"outlet={outlet} but pump={pump} — should always match",
                            row,
                        ))

        return alerts

    def _alert(self, rule: str, detail: str, row: dict) -> dict:
        return {
            "rule":       rule,
            "detail":     detail,
            "timestamp":  row.get("timestamp"),
            "experiment": row.get("experiment"),
        }

    @classmethod
    def from_file(cls, baseline_path: str, enabled_rules: set = None):
        with open(baseline_path, "r") as f:
            baseline = json.load(f)
        return cls(baseline, enabled_rules)