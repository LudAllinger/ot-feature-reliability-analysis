import pandas as pd

df = pd.read_csv("logs/merged/attack.csv")
attack = df.copy()

threshold = 90

interval = (attack.index >= 5000) & (attack.index <= 5050)

attack.loc[5000, "water_level"] = 115

attack.to_csv("logs/attacks/sensor-spoofing.csv", index=False)