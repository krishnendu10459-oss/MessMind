"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: ml_engine/preprocess.py
Description: Data preprocessing, cleaning, feature encoding, and leakage prevention.
=============================================================================
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "synthetic_mess_data.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_mess_data.csv"
PREPROCESSOR_PATH = BASE_DIR / "ml_engine" / "saved_models" / "preprocessor.joblib"

# Feature definitions to strictly PREVENT TARGET LEAKAGE
CATEGORICAL_FEATURES = ["day_of_week", "meal_type", "menu_name", "menu_category"]
NUMERICAL_FEATURES = ["attendance", "is_weekend", "month", "is_exam_season", "is_vacation"]
TARGET_FEATURE = "consumed_meals"

# Leakage fields that MUST NOT be fed to the model at prediction time
LEAKAGE_COLUMNS = ["prepared_meals", "wasted_meals", "waste_percentage"]


def load_and_clean_data(file_path: Path) -> pd.DataFrame:
    """Load raw dataset, handle missing values, duplicates, and validate data types."""
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {file_path}")

    df = pd.read_csv(file_path)
    initial_count = len(df)

    # 1. Deduplication
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"ℹ️ Removed {duplicates_removed} duplicate rows.")

    # 2. Handle missing values
    # For numerical columns, fill with median; for categorical, fill with mode or 'Unknown'
    for col in NUMERICAL_FEATURES:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    for col in CATEGORICAL_FEATURES:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna("Unknown")

    # 3. Ensure correct types
    df["attendance"] = df["attendance"].astype(int)
    df["consumed_meals"] = df["consumed_meals"].astype(int)
    df["is_weekend"] = df["is_weekend"].astype(int)
    df["month"] = df["month"].astype(int)
    df["is_exam_season"] = df["is_exam_season"].astype(int)
    df["is_vacation"] = df["is_vacation"].astype(int)
    
    if "prepared_meals" in df.columns:
        df["prepared_meals"] = df["prepared_meals"].astype(int)
    if "wasted_meals" in df.columns:
        df["wasted_meals"] = df["wasted_meals"].astype(int)

    return df


def build_preprocessor() -> ColumnTransformer:
    """
    Construct a scikit-learn ColumnTransformer.
    Uses OneHotEncoder with handle_unknown='ignore' to guarantee that new/unseen menu items
    during live prediction will never crash the system.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
            (
                "num",
                StandardScaler(),
                NUMERICAL_FEATURES,
            ),
        ],
        remainder="drop",  # Drop other columns to prevent accidental leakage
    )
    return preprocessor


def preprocess_and_save():
    print("=" * 60)
    print("🧹 Preprocessing Mess Consumption Dataset...")
    print("=" * 60)

    # Ensure target directories exist
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREPROCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = load_and_clean_data(RAW_DATA_PATH)
    print(f"📊 Dataset loaded: {len(df)} records.")

    # Check for target leakage
    print("🔒 Checking target leakage prevention:")
    print(f"   Target: '{TARGET_FEATURE}'")
    print(f"   Excluded leak columns: {LEAKAGE_COLUMNS}")
    print(f"   Allowed Input Features: {CATEGORICAL_FEATURES + NUMERICAL_FEATURES}")

    # Build and fit preprocessor
    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    preprocessor = build_preprocessor()
    preprocessor.fit(X)

    # Save fitted preprocessor
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    print(f"💾 Preprocessor object saved to: {PREPROCESSOR_PATH}")

    # Save cleaned dataset for auditing and records
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"💾 Cleaned dataset saved to: {PROCESSED_DATA_PATH}")

    return df, preprocessor


if __name__ == "__main__":
    preprocess_and_save()
