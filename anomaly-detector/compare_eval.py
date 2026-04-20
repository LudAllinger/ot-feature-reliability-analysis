# compare_eval.py
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from anomalyDetector import AnomalyDetector, ALL_RULES

BASE       = Path(__file__).resolve().parent.parent
BASELINE   = Path(__file__).resolve().parent / "baseline.json"
OUTPUT_DIR = BASE / "logs" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT     = OUTPUT_DIR / "ground_truth_comparison.json"

detector = AnomalyDetector.from_file(str(BASELINE))

GROUND_TRUTH = {
    "normal": {
        "description":   "Clean normal capture — no attacks injected",
        "modified_rows": [],
        "changed_columns": [],
        "expected_rule": "None",
        "is_normal":     True,
        "csv":           BASE / "logs" / "merged" / "normal.csv",
    },
    "DoS": {
        "description":   "packet_count and avg_packet_rate doubled, avg_interval_since_last halved — simulates network flood",
        "modified_rows": list(range(10000, 10051)),  # 51 rows
        "changed_columns": ["packet_count", "avg_packet_rate", "avg_interval_since_last"],
        "expected_rule": "PACKET_COUNT_ANOMALY + INTERVAL_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "DoS.csv",
    },
    "injection": {
        "description":   "pump forced True, outlet forced False — simulates unauthorized command injection forcing pump on with outlet closed",
        "modified_rows": list(range(1200, 1261)),  # 61 rows
        "changed_columns": ["pump", "outlet"],
        "expected_rule": "PUMP_STATE_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "injection.csv",
    },
    "MitM": {
        "description":   "inlet and outlet both forced True — simulates MitM attack forcing both valves open simultaneously",
        "modified_rows": list(range(5000, 5051)),  # 51 rows
        "changed_columns": ["inlet", "outlet"],
        "expected_rule": "VALVE_STATE_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "MitM.csv",
    },
    "replay": {
        "description":   "rows 1400-1460 replaced with rows 100-160 — simulates replay attack retransmitting earlier valid traffic",
        "modified_rows": list(range(1400, 1461)),  # 61 rows
        "changed_columns": ["all columns"],
        "expected_rule": "None — replayed valid data is behaviorally identical to normal",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "replay.csv",
    },
    "packetCount": {
        "description":   "packet_count tripled — simulates aggressive packet flood targeting network layer only",
        "modified_rows": list(range(15000, 15051)),  # 51 rows
        "changed_columns": ["packet_count"],
        "expected_rule": "PACKET_COUNT_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "packetCount.csv",
    },
    "sensor-spoofing": {
        "description":   "water_level set to 115 at row 5000 — simulates sensor spoofing reporting physically impossible value",
        "modified_rows": [5000],  # 1 row only
        "changed_columns": ["water_level"],
        "expected_rule": "WATER_LEVEL_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "sensor-spoofing.csv",
    },
    "timings": {
        "description":   "avg_interval_since_last multiplied by random factor 1.0-2.0 over 11 rows at random entrypoint — simulates timing manipulation",
        "modified_rows": None,  # dynamic — entrypoint is random, determined at generation time
        "changed_columns": ["avg_interval_since_last"],
        "expected_rule": "INTERVAL_ANOMALY",
        "is_normal":     False,
        "csv":           BASE / "logs" / "attacks" / "timings.csv",
    },
}

# ── Run evaluation ───────────────────────────────────────────────────
results = {}

print(f"\n{'Scenario':<18} {'TP':>6} {'FN':>6} {'FP':>6} {'Precision':>10} {'Recall':>8} {'F1':>8}")
print("-" * 70)

for scenario, truth in GROUND_TRUTH.items():
    csv_path = truth["csv"]
    if not csv_path.exists():
        print(f"  SKIPPED — {csv_path.name} not found")
        continue

    df   = pd.read_csv(csv_path)
    rows = df.to_dict(orient="records")

    all_alerts   = []
    alerted_rows = set()
    for i, row in enumerate(rows):
        alerts = detector.check(row)
        if alerts:
            all_alerts.extend(alerts)
            alerted_rows.add(i)

    if truth["is_normal"]:
        true_positives  = set()
        false_negatives = set()
        false_positives = alerted_rows
        expected_rows   = set()
        precision = 0.0
        recall    = 0.0
        f1        = 0.0

    elif truth["modified_rows"] is None:
        # timings — unknown ground truth due to random entrypoint
        # we can only report total alerts, not TP/FN/FP
        true_positives  = set()
        false_negatives = set()
        false_positives = set()
        expected_rows   = set()
        precision = 0.0
        recall    = 0.0
        f1        = 0.0

    else:
        expected_rows   = set(truth["modified_rows"])
        true_positives  = expected_rows & alerted_rows
        false_negatives = expected_rows - alerted_rows
        false_positives = alerted_rows - expected_rows
        precision = len(true_positives) / len(alerted_rows) if alerted_rows else 0.0
        recall    = len(true_positives) / len(expected_rows) if expected_rows else 0.0
        f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    by_rule = {}
    for alert in all_alerts:
        rule = alert["rule"]
        by_rule[rule] = by_rule.get(rule, 0) + 1

    results[scenario] = {
        "description":   truth["description"],
        "expected_rule": truth["expected_rule"],
        "ground_truth": {
            "total_rows":          len(rows),
            "modified_rows_count": len(expected_rows),
            "modified_row_range":  f"{min(expected_rows)}-{max(expected_rows)}" if expected_rows else "N/A (dynamic or none)",
            "changed_columns":     truth["changed_columns"],
        },
        "detection": {
            "total_alerts":       len(all_alerts),
            "alerted_rows_count": len(alerted_rows),
            "alerts_by_rule":     by_rule,
        },
        "evaluation": {
            "true_positives":     len(true_positives),
            "false_negatives":    len(false_negatives),
            "false_positives":    len(false_positives),
            "true_negatives":     len(rows) - len(true_positives) - len(false_negatives) - len(false_positives),
            "precision":          round(precision, 4),
            "recall":             round(recall, 4),
            "f1_score":           round(f1, 4),
            "detection_rate_pct": round(recall * 100, 2),
        },
    }

    note = " (dynamic entrypoint — TP/FN/FP not computed)" if truth["modified_rows"] is None else ""
    print(f"{scenario:<18} {len(true_positives):>6} {len(false_negatives):>6} "
          f"{len(false_positives):>6} {precision:>9.1%} {recall:>8.1%} {f1:>8.4f}{note}")

with open(OUTPUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to: {OUTPUT}")

# ── Plot ─────────────────────────────────────────────────────────────
def plot(results: dict, save_dir: Path):
    # Exclude timings from main plots since ground truth is unknown
    plot_scenarios = [s for s in results if results[s]["ground_truth"]["modified_rows_count"] > 0
                      or results[s]["evaluation"]["false_positives"] > 0
                      or s == "normal"]

    scenarios = plot_scenarios
    precision = [results[s]["evaluation"]["precision"] * 100 for s in scenarios]
    recall    = [results[s]["evaluation"]["recall"] * 100    for s in scenarios]
    f1        = [results[s]["evaluation"]["f1_score"] * 100  for s in scenarios]
    tp        = [results[s]["evaluation"]["true_positives"]  for s in scenarios]
    fn        = [results[s]["evaluation"]["false_negatives"] for s in scenarios]
    fp        = [results[s]["evaluation"]["false_positives"] for s in scenarios]
    expected  = [results[s]["ground_truth"]["modified_rows_count"] for s in scenarios]

    x     = np.arange(len(scenarios))
    width = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle(
        "Rule-Based Anomaly Detection — Ground Truth Comparison",
        fontsize=13, fontweight="bold"
    )

    # ── Plot 1: Precision, Recall, F1 ───────────────────────────────
    ax1 = axes[0]
    b1  = ax1.bar(x - width, precision, width, label="Precision",
                  color="#4C72B0", edgecolor="white", linewidth=0.8)
    b2  = ax1.bar(x,          recall,   width, label="Recall",
                  color="#DD8452", edgecolor="white", linewidth=0.8)
    b3  = ax1.bar(x + width,  f1,       width, label="F1 Score",
                  color="#55A868", edgecolor="white", linewidth=0.8)
    ax1.set_title("Precision, Recall and F1 Score\nper scenario", fontsize=11)
    ax1.set_ylabel("Score (%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=8, rotation=30, ha="right")
    ax1.set_ylim(0, 115)
    ax1.axhline(100, color="green", linestyle="--", linewidth=1,
                alpha=0.5, label="100%")
    ax1.legend(fontsize=9)
    for bars in [b1, b2, b3]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2,
                         h + 1.5, f"{h:.0f}%",
                         ha="center", va="bottom", fontsize=7, fontweight="bold")

    # ── Plot 2: TP / FN / FP stacked ────────────────────────────────
    ax2  = axes[1]
    b_tp = ax2.bar(x, tp, width=0.5, label="True positives",
                   color="#55A868", edgecolor="white", linewidth=0.8)
    b_fn = ax2.bar(x, fn, width=0.5, bottom=tp,
                   label="False negatives",
                   color="#DD8452", edgecolor="white", linewidth=0.8)
    b_fp = ax2.bar(x, fp, width=0.5,
                   bottom=[t + f for t, f in zip(tp, fn)],
                   label="False positives",
                   color="#C44E52", edgecolor="white", linewidth=0.8)
    ax2.plot(x, expected, "k--o", linewidth=1.5, markersize=5,
             label="Expected (ground truth)", zorder=5)
    ax2.set_title("Detection breakdown\n(TP / FN / FP vs ground truth)", fontsize=11)
    ax2.set_ylabel("Number of rows")
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, fontsize=8, rotation=30, ha="right")
    ax2.legend(fontsize=9)
    for i, (t, f, p) in enumerate(zip(tp, fn, fp)):
        total = t + f + p
        if total > 0:
            ax2.text(i, total + 0.5, str(total),
                     ha="center", va="bottom", fontsize=8, fontweight="bold")

    # ── Plot 3: False positive rate ──────────────────────────────────
    ax3        = axes[2]
    total_rows = [results[s]["ground_truth"]["total_rows"] for s in scenarios]
    fp_rate    = [fp[i] / total_rows[i] * 100 for i in range(len(scenarios))]
    colors     = ["#55A868" if s == "normal" else "#4C72B0" for s in scenarios]
    bars3      = ax3.bar(x, fp_rate, width=0.5, color=colors,
                         edgecolor="white", linewidth=0.8)
    ax3.set_title("False positive rate\n(FP as % of total rows)", fontsize=11)
    ax3.set_ylabel("False positive rate (%)")
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenarios, fontsize=8, rotation=30, ha="right")
    ax3.axhline(0, color="green", linestyle="--", linewidth=1,
                alpha=0.5, label="Target: 0%")
    ax3.legend(fontsize=9)
    for bar, rate in zip(bars3, fp_rate):
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 h + 0.05, f"{rate:.2f}%",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    plt.savefig(save_dir / "ground_truth_comparison.png", dpi=150, bbox_inches="tight")
    plt.savefig(save_dir / "ground_truth_comparison.pdf", bbox_inches="tight")
    print(f"Plot saved: {save_dir / 'ground_truth_comparison.png'}")
    plt.show()


plot(results, OUTPUT_DIR)