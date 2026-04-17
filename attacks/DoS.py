import pandas as pd

df = pd.read_csv("logs/merged/normal/normal.csv")
attack = df.copy()

attack.loc[15000:15050, "packet_count"] *= 1.5
attack.loc[15000:15050, "avg_packet_rate"] *= 1.5
attack.loc[15000:15050, "avg_interval_since_last"] /= 1.5

attack.to_csv("logs/attacks/DoS.csv", index=False)