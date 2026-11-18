"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: ml_engine/evaluate.py
Description: Evaluates saved Random Forest model, runs sanity checks on
unseen edge cases, and prints a formatted viva-ready model summary.
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
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml_engine.preprocess import (
    load_and_clean_data,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_FEATURE,
    RAW_DATA_PATH,
)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml_engine" / "saved_models" / "random_forest_model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "ml_engine" / "saved_models" / "preprocessor.joblib"
METRICS_PATH = BASE_DIR / "ml_engine" / "saved_models" / "model_metrics.json"


def evaluate_system():
    print("=" * 65)
    print("📈 AI Model Evaluation & Validation Suite")
    print("=" * 65)

    if not MODEL_PATH.exists() or not PREPROCESSOR_PATH.exists():
        print("❌ Model or preprocessor artifacts not found. Please train first.")
        return False

    # 1. Load artifacts
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print(f"✅ Loaded model: {type(model).__name__}")
    print(f"✅ Loaded preprocessor: {type(preprocessor).__name__}")

    # 2. Load dataset
    df = load_and_clean_data(RAW_DATA_PATH)
    feature_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    X = df[feature_cols]
    y = df[TARGET_FEATURE]

    # Transform
    X_transformed = preprocessor.transform(X)
    y_pred = model.predict(X_transformed)

    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    print("\n" + "-" * 65)
    print("🎯 Full Dataset Validation Metrics:")
    print(f"   • Mean Absolute Error (MAE)   : {mae:.2f} meals")
    print(f"   • Root Mean Squared Error (RMSE): {rmse:.2f} meals")
    print(f"   • R² Score                    : {r2:.4f}")
    print("-" * 65)

    # 3. Test on Unseen Realistic Test Scenarios
    print("\n🧪 Testing 3 Realistic Unseen Edge Cases:")
    test_cases = [
        {
            "name": "Case A: Regular Weekday Lunch with Popular Feast",
            "date": "2026-11-18",
            "day_of_week": "Wednesday",
            "meal_type": "Lunch",
            "menu_name": "Paneer Butter Masala & Naan/Rice",
            "menu_category": "Special Feast",
            "attendance": 550,
            "is_weekend": 0,
            "month": 11,
            "is_exam_season": 1,
            "is_vacation": 0,
        },
        {
            "name": "Case B: Weekend Dinner with Low Turnout Menu",
            "date": "2026-11-22",
            "day_of_week": "Sunday",
            "meal_type": "Dinner",
            "menu_name": "Plain Dal Khichdi & Curd",
            "menu_category": "Light Meal",
            "attendance": 320,
            "is_weekend": 1,
            "month": 11,
            "is_exam_season": 1,
            "is_vacation": 0,
        },
        {
            "name": "Case C: Vacation Period Breakfast",
            "date": "2026-07-15",
            "day_of_week": "Wednesday",
            "meal_type": "Breakfast",
            "menu_name": "Idli & Vada with Chutney",
            "menu_category": "South Indian",
            "attendance": 140,
            "is_weekend": 0,
            "month": 7,
            "is_exam_season": 0,
            "is_vacation": 1,
        },
    ]

    for tc in test_cases:
        df_tc = pd.DataFrame([tc])[feature_cols]
        tc_transformed = preprocessor.transform(df_tc)
        pred_val = int(round(model.predict(tc_transformed)[0]))
        # Logical check
        assert pred_val <= tc["attendance"], f"Prediction {pred_val} exceeds attendance {tc['attendance']}!"
        recommended_cook = int(math_ceil(pred_val * 1.05))

        print(f"\n   [{tc['name']}]")
        print(f"   Expected Attendance   : {tc['attendance']} students")
        print(f"   Predicted Consumption : {pred_val} meals")
        print(f"   Recommended To Cook   : {recommended_cook} meals (5% safety cushion)")
        print(f"   Calculated Buffer     : {recommended_cook - pred_val} meals")

    print("\n✅ All validation checks and edge-case assertions PASSED!")
    return True


def math_ceil(val):
    import math
    return math.ceil(val)


if __name__ == "__main__":
    evaluate_system()
