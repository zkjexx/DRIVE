import pandas as pd
import numpy as np


def generate_2026_predictions(df_historical, model, sigma_res, historical_stats):
    """
    Generate recursive monthly dengue forecasts for 2026.

    Parameters
    ----------
    df_historical : DataFrame
        Historical dataset (2023–2025) with engineered features.

    model : RandomForestRegressor
        Trained Random Forest model.

    sigma_res : float
        Residual standard deviation.

    historical_stats : DataFrame
        Barangay historical mean and standard deviation.

    Returns
    -------
    DataFrame
    """

    # ---------------------------------
    # December 2025 state
    # ---------------------------------

    dec2025 = df_historical[
        df_historical["YearMonth"] == "2025-12-01"
    ].copy()

    last_state = dec2025[
        [
            "Barangay",
            "Cases",
            "cases_lag1",
            "cases_lag2",
            "cases_roll3",
            "PopDensity",
        ]
    ].copy()

    # ---------------------------------
    # Monthly climate averages
    # ---------------------------------

    climate_avg = (
        df_historical.groupby("Month")
        .agg(
            {
                "Rainfall": "mean",
                "Temp": "mean",
                "MinTemp": "mean",
                "Humidity": "mean",
                "WindSpeed": "mean",
            }
        )
        .reset_index()
    )

    # ---------------------------------
    # Population Projection
    # ---------------------------------

    pop_projection = {}

    for barangay in df_historical["Barangay"].unique():

        b = df_historical[
            df_historical["Barangay"] == barangay
        ].sort_values("Year")

        pop2024 = b[b["Year"] == 2024]["PopDensity"].iloc[-1]
        pop2025 = b[b["Year"] == 2025]["PopDensity"].iloc[-1]

        increase = pop2025 - pop2024

        pop_projection[barangay] = pop2025 + increase

    # ---------------------------------
    # Recursive Forecasting
    # ---------------------------------

    predictions = []

    for _, row in last_state.iterrows():

        barangay = row["Barangay"]

        last3 = [
            row["cases_lag2"],
            row["cases_lag1"],
            row["Cases"],
        ]

        mu = historical_stats.loc[
            historical_stats["Barangay"] == barangay,
            "mean",
        ].values[0]

        sigma = historical_stats.loc[
            historical_stats["Barangay"] == barangay,
            "std",
        ].values[0]

        popdensity = pop_projection[barangay]

        for month in range(1, 13):

            weather = climate_avg[
                climate_avg["Month"] == month
            ].iloc[0]

            feature = pd.DataFrame(
                [
                    {
                        "cases_lag1": last3[-1],
                        "cases_lag2": last3[-2],
                        "cases_roll3": np.mean(last3),
                        "month_sin": np.sin(2 * np.pi * month / 12),
                        "month_cos": np.cos(2 * np.pi * month / 12),
                        "rainy_season": 1 if month in [6, 7, 8, 9] else 0,
                        "Rainfall": weather["Rainfall"],
                        "Temp": weather["Temp"],
                        "MinTemp": weather["MinTemp"],
                        "Humidity": weather["Humidity"],
                        "WindSpeed": weather["WindSpeed"],
                        "PopDensity": popdensity,
                    }
                ]
            )

            prediction = model.predict(feature)[0]

            prediction = max(0, int(round(prediction)))

            lower = max(0, prediction - 1.96 * sigma_res)
            upper = prediction + 1.96 * sigma_res

            if upper < mu:
                risk = "Safe"
            elif upper < mu + 0.5 * sigma:
                risk = "Moderate"
            elif upper < mu + sigma:
                risk = "High"
            else:
                risk = "Extreme"

            predictions.append(
                {
                    "Barangay": barangay,
                    "YearMonth": f"2026-{month:02d}",
                    "Predicted_Cases": prediction,
                    "Lower95": round(lower, 2),
                    "Upper95": round(upper, 2),
                    "Historical_Mean": round(mu, 2),
                    "Historical_SD": round(sigma, 2),
                    "Risk_Level": risk,
                }
            )

            # Recursive update
            last3.append(prediction)
            last3.pop(0)

    return pd.DataFrame(predictions)