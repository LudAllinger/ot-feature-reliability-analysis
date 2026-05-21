import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[900:950, "packet_count"] = 10

attack.to_csv("logs/attacks/packetCount.csv", index=False)