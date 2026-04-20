import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[15000:15050, "packet_count"] *= 3

attack.to_csv("logs/attacks/packetCount.csv", index=False)