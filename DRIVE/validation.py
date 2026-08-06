import pandas as pd
import numpy as np

# =========================
# DAY 1 – Environment & Data Validation
# =========================

df = pd.read_excel("dengue_data.xlsx")

print(df.columns.tolist())
print(df.isnull().sum())


# =========================
# DAY 2 – Data Cleaning
# =========================

# Task 1 – Remove duplicates
df = df.drop_duplicates()

# Task 2 – Check missing values → forward-fill
df = df.sort_values(["Barangay", "YearMonth"])
df["Cases"] = df.groupby("Barangay")["Cases"].ffill()

# Task 3 – Standardise date format
df["YearMonth"] = pd.to_datetime(df["YearMonth"])

# Task 4 – Extract Year and Month
df["Year"] = df["YearMonth"].dt.year
df["Month"] = df["YearMonth"].dt.month

# Task 5 – Verify barangay names
print(df["Barangay"].unique())


# =========================
# DAY 3 – Feature Engineering
# =========================

# Task 1 – Add lagged cases
df["cases_lag1"] = df.groupby("Barangay")["Cases"].shift(1)
df["cases_lag2"] = df.groupby("Barangay")["Cases"].shift(2)

# Task 2 – Add rolling average
df["cases_roll3"] = df.groupby("Barangay")["Cases"].transform(
    lambda x: x.rolling(3, min_periods=1).mean()
)

# Task 3 – Add cyclical month encoding
df["month_sin"] = np.sin(2 * np.pi * df["Month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["Month"] / 12)

# Task 4 – Add rainy season indicator
df["rainy_season"] = df["Month"].apply(
    lambda m: 1 if m in [6, 7, 8, 9] else 0
)

# Task 5 – Drop rows with NaN
df = df.dropna().reset_index(drop=True)


# =========================
# DAY 4 – Define Feature Set
# =========================

features = [
    "cases_lag1",
    "cases_lag2",
    "cases_roll3",
    "month_sin",
    "month_cos",
    "rainy_season",
    "Rainfall",
    "Temp",
    "MinTemp",
    "Humidity",
    "WindSpeed",
    "PopDensity"
]

print(features)


# =========================
# DAY 5 – Data Splitting
# =========================

# Task 1 – Train: 2023–2024
train = df[df["Year"] < 2025]

# Task 2 – Validation: 2025
val = df[df["Year"] == 2025]

# Task 3 – Save splits
train.to_csv("train.csv", index=False)
val.to_csv("val.csv", index=False)

print("Train shape:", train.shape)
print("Validation shape:", val.shape)