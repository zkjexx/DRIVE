import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# ================================================================
# 1. LOAD DATA
# ================================================================
train = pd.read_csv("train.csv")          # 2023–2024
val   = pd.read_csv("val.csv")            # 2025

# ================================================================
# 2. DEFINE FEATURES (MUST MATCH CHAPTER 3)
# ================================================================
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

X_train = train[features]
y_train = train["Cases"]
X_val = val[features]
y_val = val["Cases"]

print(f"Training set: {len(X_train)} rows")
print(f"Validation set: {len(X_val)} rows")

# ================================================================
# 3. HYPERPARAMETER TUNING (GridSearchCV) – DAY 6
# ================================================================
param_grid = {
    "n_estimators": [50, 100, 200, 500],
    "max_depth": [5, 10, 15, 20, None],
    "min_samples_leaf": [1, 2, 4, 8],
    "max_features": ["sqrt", "log2", None]
}

grid = GridSearchCV(
    RandomForestRegressor(random_state=42),
    param_grid,
    cv=5,
    scoring="neg_mean_absolute_error",
    n_jobs=-1
)

grid.fit(X_train, y_train)

best_model = grid.best_estimator_
print("\n✅ Best parameters:", grid.best_params_)
print("✅ Best cross‑validated MAE:", -grid.best_score_)

# ================================================================
# 4. PREDICT ON VALIDATION SET (2025) – DAY 7
# ================================================================
y_pred = best_model.predict(X_val)

# ================================================================
# 5. COMPUTE VALIDATION METRICS
# ================================================================

# --- MAE (Equation 5) ---
mae = mean_absolute_error(y_val, y_pred)
print(f"\n📊 MAE on 2025 data: {mae:.2f} cases")

# --- RMSE (Equation 6) ---
rmse = np.sqrt(mean_squared_error(y_val, y_pred))
print(f"📊 RMSE on 2025 data: {rmse:.2f} cases")

# --- Residuals and σ_res (Equation 3) ---
residuals = y_val - y_pred
sigma_res = np.std(residuals)
print(f"📊 Residual Std (σ_res): {sigma_res:.2f}")

# ================================================================
# 6. SAVE MODEL AND σ_res FOR LATER USE
# ================================================================
joblib.dump(best_model, "rf_model_tuned.pkl")
np.save("sigma_res.npy", sigma_res)

print("\n✅ Model saved as 'rf_model_tuned.pkl'")
print("✅ Sigma_res saved as 'sigma_res.npy'")

# ================================================================
# 7. OPTIONAL: ACTUAL VS PREDICTED SCATTER PLOT
# ================================================================
plt.figure(figsize=(8, 6))
plt.scatter(y_val, y_pred, alpha=0.6, color='steelblue')
plt.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'r--', lw=2)
plt.xlabel('Actual Cases')
plt.ylabel('Predicted Cases')
plt.title(f'Random Forest Validation (2025)\nMAE = {mae:.2f}, RMSE = {rmse:.2f}')
plt.tight_layout()
plt.savefig('validation_scatter.png', dpi=150)
plt.show()

# ================================================================
# 8. PRINT FINAL SUMMARY
# ================================================================
print("\n" + "="*50)
print("VALIDATION PERFORMANCE SUMMARY")
print("="*50)
print(f"MAE  (Mean Absolute Error)     : {mae:.2f} cases")
print(f"RMSE (Root Mean Square Error)  : {rmse:.2f} cases")
print(f"σ_res (Residual Std Dev)       : {sigma_res:.2f}")
print("="*50)