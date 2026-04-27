import pandas as pd
import numpy as np
import random as rd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

interval = (attack.index >= 50000) & (attack.index <= 50050)

attack.loc[interval, "avg_interval_since_last"] *= np.random.uniform(1.0, 2.0, size=interval.sum())

attack.to_csv("logs/attacks/timings.csv", index=False)