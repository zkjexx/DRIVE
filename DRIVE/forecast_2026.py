import pandas as pd
import numpy as np
import joblib

from forecast_utils import generate_2026_predictions
from utils import compute_historical_stats


# ==========================================
# LOAD DATA
# ==========================================

train = pd.read_csv(
    "train.csv"
)

val = pd.read_csv(
    "val.csv"
)


historical_data = pd.concat(
    [
        train,
        val
    ],
    ignore_index=True
)



# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load(
    "rf_model.pkl"
)


sigma_res = np.load(
    "sigma_res.npy"
)



# ==========================================
# HISTORICAL STATISTICS
# ==========================================

historical_stats = compute_historical_stats(
    train
)



# ==========================================
# GENERATE 2026 FORECAST
# ==========================================

predictions = generate_2026_predictions(

    df_historical=historical_data,

    model=model,

    sigma_res=sigma_res,

    historical_stats=historical_stats

)



# ==========================================
# SAVE OUTPUT
# ==========================================

predictions.to_csv(
    "predictions_2026_final_new.csv",
    index=False
)

# ==========================================
# RESULTS
# ==========================================

print("\n========== FORECAST COMPLETE ==========\n")

print(predictions.head())


print(
    f"\nTotal predictions: {len(predictions)}"
)


print(
    "\nSaved: predictions_2026_final.csv"
)


print(
    "\nRisk Distribution:"
)


if "Risk_Level" in predictions.columns:

    print(
        predictions["Risk_Level"].value_counts()
    )

else:

    print(
        "Risk_Level column not found"
    )