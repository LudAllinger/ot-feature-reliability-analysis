from baseline import BaselineBuilder
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
LOGS = BASE / "logs"
builder  = BaselineBuilder()
baseline = builder.build(LOGS / "merged" / "normal.csv")
builder.save(baseline, Path(__file__).resolve().parent / "baseline.json")

print(json.dumps(baseline, indent=2))