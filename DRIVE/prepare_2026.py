import pandas as pd

# Load all available data
train = pd.read_csv("train.csv")
val = pd.read_csv("val.csv")

# Combine historical data
df = pd.concat([train, val], ignore_index=True)

# Monthly climate averages
climate_avg = (
    df.groupby("Month")[[
        "Rainfall",
        "Temp",
        "MinTemp",
        "Humidity",
        "WindSpeed"
    ]]
    .mean()
    .reset_index()
)

# Save
climate_avg.to_csv("climate_avg_2026.csv", index=False)

print("Monthly climate averages created.")
print(climate_avg)