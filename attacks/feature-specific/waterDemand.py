import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

interval = (attack.index >= 5000) & (attack.index <= 5050)

attack.loc[1000:1010, "water_demand"] = 5

attack.to_csv("logs/attacks/waterDemand.csv", index=False)