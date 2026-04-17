import pandas as pd

df = pd.read_csv("logs/merged/normal/normal.csv")
attack = df.copy()

attack.loc[1400:1460] = df.loc[100:160].values

attack.to_csv("logs/attacks/replay.csv", index=False)