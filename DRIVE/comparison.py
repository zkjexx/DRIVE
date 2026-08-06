import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error
from scipy.stats import ttest_rel

# Load datasets
train_df = pd.read_csv("train.csv")
val_df = pd.read_csv("val.csv")

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

# Validation features and target
X_val = val_df[features]
y_val = val_df["Cases"]

# Load final Random Forest model
model = joblib.load("rf_model.pkl")

# =========================
# Task 1 – Historical Mean Baseline (from training data)
# =========================
historical_mean = (
    train_df.groupby("Barangay")["Cases"]
    .mean()
    .rename("baseline")
)

val_df = val_df.merge(historical_mean, on="Barangay")
baseline_pred = val_df["baseline"]

# =========================
# Task 2 – Random Forest predictions
# =========================
rf_pred = model.predict(X_val)

# =========================
# Task 3 – Compute MAE
# =========================
mae_rf = mean_absolute_error(y_val, rf_pred)
mae_baseline = mean_absolute_error(y_val, baseline_pred)

# =========================
# Task 4 – Paired t-test
# Compare absolute prediction errors
# =========================
rf_errors = abs(y_val - rf_pred)
baseline_errors = abs(y_val - baseline_pred)

t_stat, p_value = ttest_rel(
    baseline_errors,
    rf_errors,
    alternative="greater"
)

# =========================
# Task 5 – Print results
# =========================
print(f"MAE (Random Forest): {mae_rf:.2f}")
print(f"MAE (Baseline): {mae_baseline:.2f}")
print(f"Improvement: {mae_baseline - mae_rf:.2f} cases/month")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.01:
    print("✅ Random Forest is significantly better than the baseline (p < 0.01)")
else:
    print("❌ Random Forest is not significantly better than the baseline")