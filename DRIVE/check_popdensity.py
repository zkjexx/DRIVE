import pandas as pd

val = pd.read_csv("val.csv")

print(val["YearMonth"].tail())