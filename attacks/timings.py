import pandas as pd
import numpy as np
import random as rd

entrypoint = rd.randint(100, 15000)
print(f"Entry point for timing attack: {entrypoint}")

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

interval = (attack.index >= entrypoint) & (attack.index <= (entrypoint + 10))

attack.loc[interval, "avg_interval_since_last"] *= np.random.uniform(1.0, 2.0, size=interval.sum())

attack.to_csv("logs/attacks/timings.csv", index=False)