import pandas as pd

df = pd.read_csv("logs/merged/normal/normal.csv")
attack = df.copy()

attack.loc[5000:5050, "inlet"] = True
attack.loc[5000:5050, "water_level"] -= 10

attack.to_csv("logs/attacks/MitM.csv", index=False)