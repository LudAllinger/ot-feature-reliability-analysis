# run_detector.py
import json
import pandas as pd
from pathlib import Path
from anomalyDetector import AnomalyDetector, ALL_RULES, NETWORK_RULES, PROCESS_RULES

BASE       = Path(__file__).resolve().parent.parent
BASELINE   = Path(__file__).resolve().parent / "baseline.json"
OUTPUT_DIR = BASE / "logs" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Configure your run here ──────────────────────────────────────────
INPUT_CSV = BASE / "logs" / "attacks" / "packetCount.csv"
SCENARIO  = "Packet Count"
RULES     = ALL_RULES
OUTPUT_DIR  = BASE / "logs" / "results"
# ────────────────────────────────────────────────────────────────────

def next_attempt_number(output_dir: Path, scenario: str) -> int:
    """Find the next available attempt number for this scenario."""
    existing = list(output_dir.glob(f"{scenario}_attempt*.json"))
    if not existing:
        return 1
    numbers = []
    for f in existing:
        stem = f.stem  # e.g. "valve_stuck_attempt3"
        try:
            numbers.append(int(stem.split("attempt")[-1]))
        except ValueError:
            pass
    return max(numbers) + 1 if numbers else 1


# ── Setup ────────────────────────────────────────────────────────────
output_dir = Path(OUTPUT_DIR)
output_dir.mkdir(parents=True, exist_ok=True)

attempt    = next_attempt_number(OUTPUT_DIR, SCENARIO)
output_path = output_dir / f"{SCENARIO}_attempt{attempt}.json"

# ── Load and run ─────────────────────────────────────────────────────
detector = AnomalyDetector.from_file(str(BASELINE), enabled_rules=RULES)
df       = pd.read_csv(INPUT_CSV)
rows     = df.to_dict(orient="records")

all_alerts = []
for row in rows:
    all_alerts.extend(detector.check(row))

total_rows   = len(rows)
total_alerts = len(all_alerts)
alert_rate      = total_alerts / total_rows * 100 if total_rows > 0 else 0.0

# ── Console output ───────────────────────────────────────────────────
print(f"Scenario:      {SCENARIO} (attempt {attempt})")
print(f"Input:         {INPUT_CSV}")
print(f"Total rows:    {total_rows}")
print(f"Total alerts:  {total_alerts}")
print(f"Alert rate:    {alert_rate:.2f}%")
print(f"Output:        {output_path}")

if all_alerts:
    print(f"\nSample alerts (first 20):")
    for a in all_alerts[:20]:
        print(f"  [{a['rule']}] {a['detail']} @ {a['timestamp']}")

# ── Save to JSON ─────────────────────────────────────────────────────
output = {
    "metadata": {
        "scenario":     SCENARIO,
        "attempt":      attempt,
        "input_csv":    str(INPUT_CSV),
        "baseline":     str(BASELINE),
        "rules_used":   sorted(list(RULES)),
        "total_rows":   total_rows,
        "total_alerts": total_alerts,
        "alert_rate_pct": round(alert_rate, 4),
    },
    "alerts": all_alerts,
    "summary_by_rule": {},
}

# Count alerts per rule
for alert in all_alerts:
    rule = alert["rule"]
    if rule not in output["summary_by_rule"]:
        output["summary_by_rule"][rule] = 0
    output["summary_by_rule"][rule] += 1

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")