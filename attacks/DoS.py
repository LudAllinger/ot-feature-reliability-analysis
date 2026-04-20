import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

interval = (attack.index >= 10000) & (attack.index <= 10050)

attack.loc[10000:10050, "packet_count"] *= 2
attack.loc[10000:10050, "avg_packet_rate"] *= 2
attack.loc[10000:10050, "avg_interval_since_last"] /= 2

attack.to_csv("logs/attacks/DoS.csv", index=False)