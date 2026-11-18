"""
=============================================================================
Unit & Integration Tests: Machine Learning & Dataset Validation
File: tests/test_ml.py
=============================================================================
"""

import json
import os
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "synthetic_mess_data.csv"
MODEL_PATH = BASE_DIR / "ml_engine" / "saved_models" / "random_forest_model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "ml_engine" / "saved_models" / "preprocessor.joblib"
CHRONO_PATH = BASE_DIR / "ml_engine" / "saved_models" / "chronological_evaluation.json"


def test_dataset_exists_and_size():
    """Verify raw dataset exists and has at least 500 records."""
    assert RAW_DATA_PATH.exists(), f"Raw dataset not found at {RAW_DATA_PATH}"
    df = pd.read_csv(RAW_DATA_PATH)
    assert len(df) >= 500, f"Expected at least 500 records, got {len(df)}"


def test_dataset_mathematical_constraints():
    """Verify that consumed <= prepared and wasted == prepared - consumed."""
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Consumed cannot exceed prepared
    violations_consumed = df[df["consumed_meals"] > df["prepared_meals"]]
    assert len(violations_consumed) == 0, f"Found {len(violations_consumed)} records where consumed > prepared"

    # Wasted must exactly equal prepared - consumed
    violations_waste = df[df["wasted_meals"] != (df["prepared_meals"] - df["consumed_meals"])]
    assert len(violations_waste) == 0, f"Found {len(violations_waste)} records with invalid waste math"


def test_no_target_leakage_in_features():
    """Verify that feature columns do NOT include future waste or prepared counts."""
    from ml_engine.preprocess import CATEGORICAL_FEATURES, NUMERICAL_FEATURES
    all_features = set(CATEGORICAL_FEATURES + NUMERICAL_FEATURES)
    leakage_cols = {"prepared_meals", "wasted_meals", "waste_percentage"}
    assert not (all_features & leakage_cols), "Target leakage detected in input feature list!"


def test_model_and_preprocessor_artifacts_exist():
    """Ensure trained model and preprocessor are saved to disk."""
    assert MODEL_PATH.exists(), f"Model artifact missing at {MODEL_PATH}"
    assert PREPROCESSOR_PATH.exists(), f"Preprocessor artifact missing at {PREPROCESSOR_PATH}"


def test_chronological_evaluation_exists_and_valid():
    """Verify chronological evaluation results are saved and show strong performance."""
    assert CHRONO_PATH.exists(), f"Chronological evaluation artifact missing at {CHRONO_PATH}"
    with open(CHRONO_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "chronological_metrics" in data
    assert data["chronological_metrics"]["random_forest"]["r2_score"] > 0.90


def test_predictor_sanity_output():
    """Verify that MealDemandPredictor produces logically sound meal counts and statistical intervals."""
    from ml_engine.predict import MealDemandPredictor
    predictor = MealDemandPredictor()
    
    res = predictor.predict(
        date_str="2026-11-20",
        meal_type="Lunch",
        menu_name="Veg Biryani & Mirchi Ka Salan",
        attendance=500
    )
    
    assert "predicted_consumed_meals" in res
    assert "recommended_preparation" in res
    assert "prediction_interval_90" in res
    assert 0 < res["predicted_consumed_meals"] <= 500
    assert res["recommended_preparation"] >= res["predicted_consumed_meals"]
    
    pi = res["prediction_interval_90"]
    assert pi["min"] <= res["predicted_consumed_meals"] <= pi["max"]
    assert pi["tree_std"] >= 0.0


def test_predictor_handles_novel_menu():
    """Verify model gracefully handles completely unseen novel menu names."""
    from ml_engine.predict import MealDemandPredictor
    predictor = MealDemandPredictor()
    
    res = predictor.predict(
        date_str="2028-05-12",
        meal_type="Dinner",
        menu_name="Brand New Extraterrestrial Curry 999",
        attendance=400
    )
    assert 0 < res["predicted_consumed_meals"] <= 400
    assert res["recommended_preparation"] >= res["predicted_consumed_meals"]


def test_predictor_empirical_coverage_on_held_out_data():
    """
    Verify that the heuristic uncertainty range provides at least 90% empirical
    coverage on the held-out chronological test split.
    """
    import joblib
    from ml_engine.predict import MealDemandPredictor
    predictor = MealDemandPredictor()

    df = pd.read_csv(RAW_DATA_PATH)
    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.sort_values(by=["record_date", "meal_type"]).reset_index(drop=True)

    # 80/20 chronological split
    dates = sorted(df["record_date"].unique())
    split_idx = int(len(dates) * 0.8)
    split_date = dates[split_idx]
    test_df = df[df["record_date"] >= split_date]

    inside_count = 0
    total = len(test_df)

    for _, row in test_df.iterrows():
        pred = predictor.predict(
            date_str=row["record_date"].strftime("%Y-%m-%d"),
            meal_type=row["meal_type"],
            menu_name=row["menu_name"],
            attendance=int(row["attendance"])
        )
        pi = pred["prediction_interval_90"]
        actual = row["consumed_meals"]
        if pi["min"] <= actual <= pi["max"]:
            inside_count += 1

    coverage = inside_count / total
    assert coverage >= 0.90, f"Empirical coverage was {coverage:.1%}, expected at least 90%"
