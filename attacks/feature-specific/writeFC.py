import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[900:950, "write_count"] = 1


attack.to_csv("logs/attacks/writeFC.csv", index=False)