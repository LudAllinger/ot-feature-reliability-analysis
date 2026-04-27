import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[15000:15050, "avg_interval_since_last"] *= 3

attack.to_csv("logs/attacks/packetInterval.csv", index=False)