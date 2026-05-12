import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[955:1005, "avg_interval_since_last"] *= 0.6

attack.to_csv("logs/attacks/packetInterval.csv", index=False)