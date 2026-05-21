import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[900:950, "outlet"] = True
attack.loc[900:950, "pump"] = False

attack.to_csv("logs/attacks/outlet-pump.csv", index=False)