# =====================================================
# D.R.I.V.E.
# utils.py
# Core Utility Functions (Robust)
# =====================================================

import numpy as np
import pandas as pd

# =====================================================
# ADD SEASONALITY
# =====================================================

def add_seasonality(df, month_column="Month"):
    """
    Adds cyclical month features: month_sin and month_cos
    """
    df = df.copy()
    df["month_sin"] = np.sin(2 * np.pi * df[month_column] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df[month_column] / 12)
    return df


# =====================================================
# 4-LEVEL RISK CLASSIFICATION (Robust)
# =====================================================

def classify_risk_4level(cases, mu, sigma):
    """
    Classify dengue risk into 4 levels based on historical mean (mu)
    and standard deviation (sigma).
    
    Parameters:
        cases (float/int/array): Predicted cases (or upper bound)
        mu (float/int/array): Historical mean cases
        sigma (float/int/array): Historical standard deviation
    
    Returns:
        str: 'Safe', 'Moderate', 'High', or 'Extreme'
    """
    # --- Force scalars (convert Series/arrays to single values) ---
    def to_scalar(value):
        if hasattr(value, 'item'):   # numpy array or pandas Series
            return value.item()
        elif hasattr(value, 'iloc'): # pandas Series/DataFrame
            return value.iloc[0]
        else:
            return value

    cases = to_scalar(cases)
    mu = to_scalar(mu)
    sigma = to_scalar(sigma)

    # Convert to float to be safe
    cases = float(cases)
    mu = float(mu)
    sigma = float(sigma)

    # --- Classify ---
    if cases < mu:
        return "Safe"
    elif cases < mu + 0.5 * sigma:
        return "Moderate"
    elif cases < mu + sigma:
        return "High"
    else:
        return "Extreme"


# =====================================================
# HISTORICAL STATISTICS
# =====================================================

def compute_historical_stats(df):
    stats = (
        df.groupby("Barangay")["Cases"]
        .agg(mean="mean", std="std")
        .reset_index()
    )
    return stats


# =====================================================
# PREDICTION COVERAGE
# =====================================================

def calculate_prediction_coverage(actual, lower, upper):
    """
    Calculates percentage of actual values inside prediction interval.
    """
    actual = np.array(actual)
    lower = np.array(lower)
    upper = np.array(upper)
    
    covered = (actual >= lower) & (actual <= upper)
    coverage = (covered.sum() / len(actual)) * 100
    
    return round(coverage, 2)


# =====================================================
# BASELINE COMPARISON
# =====================================================

def baseline_comparison(actual, predicted):
    """
    Compares Random Forest prediction against mean baseline.
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    model_mae = np.mean(np.abs(actual - predicted))
    baseline_value = np.mean(actual)
    baseline_prediction = np.full(len(actual), baseline_value)
    baseline_mae = np.mean(np.abs(actual - baseline_prediction))
    
    return {
        "Model_MAE": round(model_mae, 2),
        "Baseline_MAE": round(baseline_mae, 2),
        "Improvement": round(baseline_mae - model_mae, 2)
    }
