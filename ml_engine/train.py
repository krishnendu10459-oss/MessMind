"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: ml_engine/train.py
Description: Trains Random Forest Regressor and baseline model on mess records.
Evaluates using MAE, RMSE, and R2. Exports model and metric artifacts.
=============================================================================
"""

import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml_engine.preprocess import (
    load_and_clean_data,
    build_preprocessor,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_FEATURE,
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    PREPROCESSOR_PATH,
)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml_engine" / "saved_models" / "random_forest_model.joblib"
METRICS_PATH = BASE_DIR / "ml_engine" / "saved_models" / "model_metrics.json"


def train_and_evaluate():
    print("=" * 65)
    print("🤖 Training Machine Learning Models for Food Waste Prediction")
    print("=" * 65)

    # 1. Load Data
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data file missing: {RAW_DATA_PATH}")

    df = load_and_clean_data(RAW_DATA_PATH)
    print(f"📊 Training records available: {len(df)}")

    # 2. Strict target & feature separation (Target Leakage Prevention)
    feature_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    X = df[feature_cols]
    y = df[TARGET_FEATURE]

    print(f"🔑 Selected Features ({len(feature_cols)}): {feature_cols}")
    print(f"🎯 Target Variable: '{TARGET_FEATURE}'")

    # 3. Proper Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, shuffle=True
    )
    print(f"📈 Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

    # 4. Feature Encoding & Transformation
    preprocessor = build_preprocessor()
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # 5. Baseline Model (Mean Dummy Regressor)
    baseline_model = DummyRegressor(strategy="mean")
    baseline_model.fit(X_train_transformed, y_train)
    baseline_pred = baseline_model.predict(X_test_transformed)

    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
    baseline_r2 = r2_score(y_test, baseline_pred)

    # 6. Primary Model: Random Forest Regressor
    rf_model = RandomForestRegressor(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train_transformed, y_train)
    rf_pred = rf_model.predict(X_test_transformed)

    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    rf_r2 = r2_score(y_test, rf_pred)

    # 7. Print Comparative Evaluation
    print("\n" + "-" * 65)
    print("📊 MODEL EVALUATION RESULTS (TEST DATASET)")
    print("-" * 65)
    print(f"{'Metric':<25} | {'Baseline (Dummy Mean)':<20} | {'Random Forest Regressor':<20}")
    print("-" * 65)
    print(f"{'Mean Absolute Error (MAE)':<25} | {baseline_mae:<20.2f} | {rf_mae:<20.2f}")
    print(f"{'Root Mean Squared Error':<25} | {baseline_rmse:<20.2f} | {rf_rmse:<20.2f}")
    print(f"{'R-squared (R²) Score':<25} | {baseline_r2:<20.4f} | {rf_r2:<20.4f}")
    print("-" * 65)

    mae_improvement = ((baseline_mae - rf_mae) / baseline_mae) * 100
    print(f"🚀 Random Forest outperforms baseline MAE by {mae_improvement:.1f}%")

    # 8. Save Serialized Artifacts
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_model, MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    print(f"💾 Trained model saved to: {MODEL_PATH}")
    print(f"💾 Preprocessor saved to: {PREPROCESSOR_PATH}")

    # 9. Save Evaluation Metrics JSON for College Reports
    metrics_data = {
        "model_name": "Random Forest Regressor",
        "algorithm": "RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42)",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "random_forest": {
            "mae": round(float(rf_mae), 2),
            "rmse": round(float(rf_rmse), 2),
            "r2_score": round(float(rf_r2), 4),
        },
        "baseline_dummy": {
            "mae": round(float(baseline_mae), 2),
            "rmse": round(float(baseline_rmse), 2),
            "r2_score": round(float(baseline_r2), 4),
        },
        "improvements": {
            "mae_reduction_percent": round(float(mae_improvement), 1)
        },
        "features_used": feature_cols,
        "target_variable": TARGET_FEATURE,
        "synthetic_data_limitations": (
            "The model is trained on a synthetic dataset reflecting estimated student attendance "
            "and menu-dependent consumption patterns. While accurate for standard college patterns, "
            "unanticipated real-world campus events (sudden holidays, hostel water disruption, food delivery discounts) "
            "may introduce variations requiring ongoing human supervision."
        ),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    print(f"📄 Metrics exported to: {METRICS_PATH}")

    # Also save cleaned dataset
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    return rf_model, preprocessor, metrics_data


if __name__ == "__main__":
    train_and_evaluate()
