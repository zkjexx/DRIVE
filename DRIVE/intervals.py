import pandas as pd
import numpy as np
import joblib

# Load validation data
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

X_val = val[features]
y_val = val["Cases"]

# Load final model and residual standard deviation
model = joblib.load("rf_model.pkl")
sigma_res = np.load("sigma_res.npy")

# Predict on validation set
y_pred_val = model.predict(X_val)

# Task 1 – Calculate prediction intervals
lower = y_pred_val - 1.96 * sigma_res
upper = y_pred_val + 1.96 * sigma_res

# Task 2 – Compute coverage
coverage = np.mean((y_val >= lower) & (y_val <= upper))

# Task 3 – Print coverage
print(f"95% Prediction Interval Coverage: {coverage:.2%}")

# Task 4 – Save result
results = pd.DataFrame({
    "YearMonth": val["YearMonth"],
    "Barangay": val["Barangay"],
    "Actual": y_val,
    "Predicted": y_pred_val,
    "Lower95": lower,
    "Upper95": upper
})

results.to_csv("prediction_intervals.csv", index=False)
print("Prediction intervals saved to prediction_intervals.csv")