import joblib
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# LOAD RANDOM FOREST MODEL
# ==========================================

rf_model = joblib.load("rf_model.pkl")


# ==========================================
# GET FEATURE NAMES
# ==========================================

features = rf_model.feature_names_in_


# ==========================================
# CREATE FEATURE IMPORTANCE TABLE
# ==========================================

importance_df = pd.DataFrame({

    "Feature": features,

    "Importance": rf_model.feature_importances_

})


# Sort from highest to lowest
importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
).reset_index(drop=True)


# Round values to 3 decimal places
importance_df["Importance"] = importance_df["Importance"].round(3)


# ==========================================
# SAVE TABLE
# ==========================================

importance_df.to_csv(
    "Table_5_Feature_Importance.csv",
    index=False
)


# ==========================================
# CREATE FIGURE 3
# ==========================================

plt.figure(figsize=(10,6))

# Reverse so highest appears at the top
plot_df = importance_df.iloc[::-1]

plt.barh(
    plot_df["Feature"],
    plot_df["Importance"]
)

plt.xlabel("Importance Score")
plt.ylabel("Predictor Variables")
plt.title("Feature Importance Analysis: Top Predictors of Dengue Incidence")

plt.tight_layout()

plt.savefig(
    "Figure_3_Feature_Importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\nFeature Importance Rankings")
print("-" * 45)
print(importance_df.to_string(index=False))

print("\nTop 3 Most Important Predictors")
print("-" * 45)
print(importance_df.head(3))

print("\n✅ Table saved as 'Table_5_Feature_Importance.csv'")
print("✅ Figure saved as 'Figure_3_Feature_Importance.png'")