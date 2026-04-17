from baseline import BaselineBuilder
import os

builder  = BaselineBuilder()
baseline = builder.build(r"C:\Users\ameli\OneDrive\Documents\thesis\thesis\anomaly-detector\src\normalAltered.csv")
builder.save(baseline, r"C:\Users\ameli\OneDrive\Documents\thesis\thesis\anomaly-detector\src\baseline.json")

import json
print(json.dumps(baseline, indent=2))