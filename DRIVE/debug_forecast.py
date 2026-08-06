# ============================================
# D.R.I.V.E. Day 11 Forecast Debugging Script
# ============================================

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# =========================
# CONFIGURATION
# =========================

MODEL_PATH = "rf_model.pkl"
DATA_PATH = "data/dengue_features.csv"

TARGET_COLUMN = "Cases"
YEAR_COLUMN = "Year"

VALIDATION_YEAR = 2025


# =========================
# LOAD MODEL AND DATA
# =========================

print("\nLoading model and dataset...")

model = joblib.load(MODEL_PATH)

df = pd.read_csv(DATA_PATH)


print("\nDataset loaded.")
print(df.head())


# =========================
# 1. CHECK MODEL FEATURES
# =========================

print("\n==============================")
print("MODEL FEATURES")
print("==============================")

model_features = list(model.feature_names_in_)

for f in model_features:
    print(f)


# =========================
# 2. CHECK DATA FEATURES
# =========================

print("\n==============================")
print("DATA FEATURES")
print("==============================")

data_features = df.columns.tolist()

for f in data_features:
    print(f)


missing = set(model_features) - set(data_features)
extra = set(data_features) - set(model_features)

print("\nMissing Features:")
print(missing)

print("\nExtra Features:")
print(extra)


# =========================
# 3. PREPARE VALIDATION DATA
# =========================

print("\nPreparing 2025 validation data...")

validation_df = df[
    df[YEAR_COLUMN] == VALIDATION_YEAR
].copy()


X_val = validation_df[model_features]
y_val = validation_df[TARGET_COLUMN]


# =========================
# 4. FEATURE VALUE CHECK
# =========================

print("\n==============================")
print("FEATURE STATISTICS")
print("==============================")

print(X_val.describe())


# =========================
# 5. RUN VALIDATION PREDICTION
# =========================

print("\nRunning 2025 prediction...")

predictions = model.predict(X_val)


results = pd.DataFrame({
    "Actual": y_val.values,
    "Predicted": predictions
})


print("\nPrediction Results:")
print(results.head(20))


# =========================
# 6. MODEL PERFORMANCE
# =========================

mae = mean_absolute_error(
    y_val,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_val,
        predictions
    )
)

r2 = r2_score(
    y_val,
    predictions
)


print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("MAE :", mae)
print("RMSE:", rmse)
print("R²  :", r2)


# =========================
# 7. CHECK BARANGAY STATISTICS
# =========================

if "Barangay" in df.columns:

    print("\n==============================")
    print("BARANGAY CASE STATISTICS")
    print("==============================")

    print(
        df.groupby("Barangay")[TARGET_COLUMN]
        .describe()
    )


# =========================
# 8. CHECK FOR EXTREME VALUES
# =========================

print("\n==============================")
print("EXTREME VALUE CHECK")
print("==============================")


for col in model_features:

    maximum = X_val[col].max()
    minimum = X_val[col].min()

    print(
        f"{col}: min={minimum}, max={maximum}"
    )


# =========================
# 9. PLOT ACTUAL VS PREDICTED
# =========================

plt.figure(figsize=(12,5))

plt.plot(
    y_val.values,
    label="Actual"
)

plt.plot(
    predictions,
    label="Predicted"
)

plt.title(
    "D.R.I.V.E. 2025 Validation: Actual vs Predicted"
)

plt.xlabel("Sample")
plt.ylabel("Dengue Cases")

plt.legend()

plt.show()


print("\n==============================")
print("DEBUGGING COMPLETE")
print("==============================")