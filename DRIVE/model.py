import pandas as pd
import numpy as np
import joblib


# =========================
# DAY 7 – Train Final Model & Compute Residuals
# =========================

# Load training and validation data
train = pd.read_csv("train.csv")
val = pd.read_csv("val.csv")

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

# Prepare data
X_train = train[features]
y_train = train["Cases"]

X_val = val[features]
y_val = val["Cases"]


# Task 1 – Train on full training set
model = joblib.load("rf_model_tuned.pkl")
model.fit(X_train, y_train)


# Task 2 – Predict on validation set (2025)
y_pred_val = model.predict(X_val)


# Task 3 – Compute residuals
residuals = y_val - y_pred_val


# Task 4 – Compute σ_res
sigma_res = np.std(residuals)


# Task 5 – Save model and σ_res
joblib.dump(model, "rf_model.pkl")
np.save("sigma_res.npy", sigma_res)


print("Residual Standard Deviation:", sigma_res)
print("Model saved as rf_model.pkl")

print("\n===== TRAINING DATA STATISTICS =====\n")

print(
    train.groupby("Barangay")["Cases"].agg(
        ["count", "mean", "std", "min", "max"]
    )
)