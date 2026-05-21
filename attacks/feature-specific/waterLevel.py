import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

attack.loc[900:950, "water_level"] = 200

attack.to_csv("logs/attacks/waterLevel.csv", index=False)