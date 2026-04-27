import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[2000:2050, "avg_packet_rate"] *= 3

attack.to_csv("logs/attacks/packetRate.csv", index=False)