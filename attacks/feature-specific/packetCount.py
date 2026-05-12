import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[950:1000, "packet_count"] = 6

attack.to_csv("logs/attacks/packetCount.csv", index=False)