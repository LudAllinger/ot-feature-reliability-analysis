import pandas as pd

df = pd.read_csv("logs/merged/normal/normal.csv")
attack = df.copy()

attack.loc[1200:1260, "pump"] = True
attack.loc[1200:1260, "outlet"] = False

attack.to_csv("logs/attacks/injection.csv", index=False)