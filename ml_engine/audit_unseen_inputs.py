"""
=============================================================================
Audit Script: Unseen Dates and Unseen Menu Names Verification
File: ml_engine/audit_unseen_inputs.py
=============================================================================
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml_engine.predict import MealDemandPredictor


def audit_novel_inputs():
    print("=" * 70)
    print("🧪 AUDIT: UNSEEN DATES & UNSEEN MENUS VERIFICATION")
    print("=" * 70)

    p = MealDemandPredictor()

    novel_scenarios = [
        {
            "scenario": "1. Far Future Date + Unseen Continental Dish",
            "date": "2028-09-15",
            "meal": "Dinner",
            "menu": "Continental Baked Lasagna & Garlic Toast",
            "attendance": 420,
        },
        {
            "scenario": "2. Leap Year Holiday + Unseen Regional Street Food",
            "date": "2028-02-29",
            "meal": "Breakfast",
            "menu": "Indori Poha Jalebi & Masala Tea",
            "attendance": 260,
        },
        {
            "scenario": "3. Unseen Festive Feast + High Attendance",
            "date": "2027-10-20",
            "meal": "Lunch",
            "menu": "Royal Awadhi Dum Biryani & Phirni",
            "attendance": 600,
        },
        {
            "scenario": "4. Arbitrary Typos & Synthetic Menu Item",
            "date": "2026-12-31",
            "meal": "Dinner",
            "menu": "Xyzabc Fusion Roll 99",
            "attendance": 350,
        },
    ]

    all_passed = True
    for item in novel_scenarios:
        res = p.predict(
            date_str=item["date"],
            meal_type=item["meal"],
            menu_name=item["menu"],
            attendance=item["attendance"],
        )
        pred = res["predicted_consumed_meals"]
        rec = res["recommended_preparation"]
        pi = res["prediction_interval_90"]

        # Assertions
        assert 0 < pred <= item["attendance"], f"Prediction {pred} out of bounds!"
        assert rec >= pred, f"Cook recommendation {rec} less than consumption {pred}!"
        assert pi["min"] <= pred <= pi["max"], f"Prediction {pred} outside interval [{pi['min']}, {pi['max']}]!"

        print(f"\n[{item['scenario']}]")
        print(f"   Date: {item['date']} | Meal: {item['meal']} | Menu: '{item['menu']}'")
        print(f"   Attendance: {item['attendance']} | Inferred Category: {res['menu_category']}")
        print(f"   Predicted Consumption: {pred} meals | Cook Rec: {rec} meals")
        print(f"   90% Prediction Interval: [{pi['min']}, {pi['max']}] (±{pi['margin_meals']} meals)")

    print("\n" + "=" * 70)
    print("✅ AUDIT RESULT: ALL UNSEEN INPUT SCENARIOS PASSED WITH VALID PREDICTIONS!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    audit_novel_inputs()
