import pandas as pd

# =========================
# DAY 9 – Risk Classification
# =========================

# Load training data
df_train = pd.read_csv("train.csv")

# Load prediction intervals
pred_df = pd.read_csv("prediction_intervals.csv")

# Task 1 – Compute μ and σ per barangay
historical_stats = (
    df_train.groupby("Barangay")["Cases"]
    .agg(["mean", "std"])
    .reset_index()
)

# Task 2 – Merge into prediction dataset
pred_df = pred_df.merge(historical_stats, on="Barangay")

# Task 3 – Define classification function
def classify_risk(row):
    ub = row["Upper95"]
    mu = row["mean"]
    sigma = row["std"]

    if ub < mu:
        return "Safe"
    elif ub < mu + 0.5 * sigma:
        return "Moderate"
    elif ub < mu + sigma:
        return "High"
    else:
        return "Extreme"

# Task 4 – Apply to upper bound
pred_df["risk_level"] = pred_df.apply(classify_risk, axis=1)

# Map to colors for Streamlit
risk_colors = {
    "Safe": "#00cc00",      # Green
    "Moderate": "#ffcc00",  # Yellow
    "High": "#ff9900",      # Orange
    "Extreme": "#ff0000"    # Red
}

# Display results
print(pred_df[[
    "YearMonth",
    "Barangay",
    "Predicted",
    "Upper95",
    "risk_level"
]].head())

# Save results
pred_df.to_csv("risk_predictions.csv", index=False)

print("Risk predictions saved to risk_predictions.csv")