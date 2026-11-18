"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: ml_engine/generate_dataset.py
Description: Generates realistic synthetic college mess records for model training.

NOTE ON DATASET NATURE:
This dataset is SYNTHETIC and generated specifically for academic research,
college project demonstration, and machine learning model validation.
Real college mess data exhibits similar patterns of student attendance,
day-of-week seasonality, and menu-popularity-driven consumption variances.
=============================================================================
"""

import csv
import os
import random
from datetime import date, timedelta
from pathlib import Path

# Fix random seed for reproducibility
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "synthetic_mess_data.csv"

# College Mess Parameters
TOTAL_ENROLLED_HOSTELLERS = 650

# Menu Categories and Popularity Factors (Consumption Rate Multipliers)
MENUS_BY_MEAL = {
    "Breakfast": [
        {"name": "Masala Dosa & Sambar", "category": "South Indian", "popularity": 0.94},
        {"name": "Poori & Aloo Sabzi", "category": "North Indian", "popularity": 0.92},
        {"name": "Aloo Paratha & Curd", "category": "North Indian", "popularity": 0.93},
        {"name": "Idli & Vada with Chutney", "category": "South Indian", "popularity": 0.86},
        {"name": "Poha & Boiled Eggs/Sprouts", "category": "Light Snacks", "popularity": 0.82},
        {"name": "Upma & Mixed Chutney", "category": "Light Snacks", "popularity": 0.76},
    ],
    "Lunch": [
        {"name": "Paneer Butter Masala & Naan/Rice", "category": "Special Feast", "popularity": 0.95},
        {"name": "Veg Biryani & Mirchi Ka Salan", "category": "Special Feast", "popularity": 0.96},
        {"name": "Rajma Masala & Steamed Rice", "category": "North Indian", "popularity": 0.91},
        {"name": "Chole Bhature & Jeera Rice", "category": "North Indian", "popularity": 0.93},
        {"name": "Dal Makhani & Roti/Rice", "category": "North Indian", "popularity": 0.89},
        {"name": "Sambhar Rice & Poriyal", "category": "South Indian", "popularity": 0.84},
        {"name": "Kadhi Pakoda & Rice", "category": "North Indian", "popularity": 0.85},
        {"name": "Mixed Veg Curry & Phulka/Dal", "category": "Regular Meal", "popularity": 0.81},
        {"name": "Lauki Kofta & Steamed Rice", "category": "Regular Meal", "popularity": 0.75},
    ],
    "Dinner": [
        {"name": "Butter Paneer & Kulcha", "category": "Special Feast", "popularity": 0.94},
        {"name": "Chicken/Mushroom Biryani Special", "category": "Special Feast", "popularity": 0.97},
        {"name": "Egg Curry / Malai Kofta & Rice", "category": "North Indian", "popularity": 0.90},
        {"name": "Dal Tadka & Phulka with Salad", "category": "Regular Meal", "popularity": 0.83},
        {"name": "Aloo Gobi & Chapati", "category": "Regular Meal", "popularity": 0.80},
        {"name": "Rasam Rice & Papad", "category": "South Indian", "popularity": 0.78},
        {"name": "Plain Dal Khichdi & Curd", "category": "Light Meal", "popularity": 0.72},
    ]
}


def is_exam_period(current_date: date) -> bool:
    """College exams typically occur in May/June and November/December."""
    return current_date.month in [5, 6, 11, 12] and (10 <= current_date.day <= 28)


def is_vacation_or_holiday(current_date: date) -> bool:
    """Mid-semester breaks (March/October) and summer/winter breaks."""
    if current_date.month in [7]:  # Summer break
        return True
    if current_date.month in [1] and current_date.day <= 10:  # Winter break
        return True
    return False


def generate_records(num_days: int = 240) -> list:
    """
    Generate synthetic daily records across 240 calendar days for Breakfast, Lunch, and Dinner.
    240 days * 3 meals/day = 720 comprehensive records.
    """
    records = []
    start_date = date(2025, 7, 1)  # Starting from academic year onset
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day_offset in range(num_days):
        cur_date = start_date + timedelta(days=day_offset)
        day_name = days_of_week[cur_date.weekday()]
        is_weekend = 1 if cur_date.weekday() >= 5 else 0
        in_exams = 1 if is_exam_period(cur_date) else 0
        in_break = 1 if is_vacation_or_holiday(cur_date) else 0

        # Base attendance depends on academic calendar
        if in_break:
            base_attendance = int(TOTAL_ENROLLED_HOSTELLERS * random.uniform(0.18, 0.30))
        elif in_exams:
            # High hostel presence during exams
            base_attendance = int(TOTAL_ENROLLED_HOSTELLERS * random.uniform(0.88, 0.98))
        elif is_weekend:
            # Significant weekend drop (students outing, visiting home)
            base_attendance = int(TOTAL_ENROLLED_HOSTELLERS * random.uniform(0.55, 0.72))
        else:
            # Regular weekday
            base_attendance = int(TOTAL_ENROLLED_HOSTELLERS * random.uniform(0.78, 0.92))

        for meal_type, menu_list in MENUS_BY_MEAL.items():
            menu_item = random.choice(menu_list)
            menu_name = menu_item["name"]
            category = menu_item["category"]
            popularity = menu_item["popularity"]

            # Meal specific attendance adjustments
            if meal_type == "Breakfast":
                meal_attendance = int(base_attendance * random.uniform(0.80, 0.90))
            elif meal_type == "Lunch":
                meal_attendance = int(base_attendance * (0.95 if not is_weekend else 0.85))
            else:  # Dinner
                meal_attendance = int(base_attendance * (0.92 if not is_weekend else 0.75))

            # Add subtle random variation (+- 3%)
            meal_attendance = max(40, int(meal_attendance * random.uniform(0.97, 1.03)))

            # Actual consumption is influenced by menu popularity & day type
            consumption_rate = popularity * random.uniform(0.96, 1.02)
            consumption_rate = min(0.99, max(0.65, consumption_rate))

            actual_consumed = int(meal_attendance * consumption_rate)

            # Mess staff prepares meals with a safety buffer (usually +8% to +20% over estimated attendance)
            # When mess operators lack an AI tool, buffer tends to be unnecessarily large (10-22%)
            cook_buffer_percentage = random.uniform(0.08, 0.22)
            prepared_meals = int(meal_attendance * (1.0 + cook_buffer_percentage))

            # HARD CONSTRAINT CHECK: Consumed meals NEVER exceed prepared meals
            if actual_consumed > prepared_meals:
                prepared_meals = actual_consumed + random.randint(2, 10)

            # STRICT CALCULATION: Wasted meals = Prepared - Consumed
            wasted_meals = prepared_meals - actual_consumed
            waste_pct = round((wasted_meals / prepared_meals) * 100, 2) if prepared_meals > 0 else 0.0

            records.append({
                "record_date": cur_date.strftime("%Y-%m-%d"),
                "day_of_week": day_name,
                "meal_type": meal_type,
                "menu_name": menu_name,
                "menu_category": category,
                "attendance": meal_attendance,
                "prepared_meals": prepared_meals,
                "consumed_meals": actual_consumed,
                "wasted_meals": wasted_meals,
                "waste_percentage": waste_pct,
                "is_weekend": is_weekend,
                "month": cur_date.month,
                "is_exam_season": in_exams,
                "is_vacation": in_break
            })

    return records


def main():
    print("=" * 60)
    print("🌱 Generating Synthetic College Mess Records...")
    print("=" * 60)
    
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = generate_records(num_days=240)
    
    fieldnames = [
        "record_date",
        "day_of_week",
        "meal_type",
        "menu_name",
        "menu_category",
        "attendance",
        "prepared_meals",
        "consumed_meals",
        "wasted_meals",
        "waste_percentage",
        "is_weekend",
        "month",
        "is_exam_season",
        "is_vacation"
    ]

    with open(RAW_DATA_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✅ Generated {len(records)} realistic daily records successfully!")
    print(f"📁 Saved to: {RAW_DATA_PATH}")

    # Integrity verification
    over_consumed = [r for r in records if r["consumed_meals"] > r["prepared_meals"]]
    inconsistent_waste = [
        r for r in records if r["wasted_meals"] != (r["prepared_meals"] - r["consumed_meals"])
    ]

    assert len(over_consumed) == 0, "Violation: Consumed meals exceed prepared meals!"
    assert len(inconsistent_waste) == 0, "Violation: Wasted meals != Prepared - Consumed!"
    print("✅ Strict mathematical constraints verified: Consumed <= Prepared and Wasted = Prepared - Consumed.")


if __name__ == "__main__":
    main()
