"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: database/seed_data.py
Description: Seeds SQLite/MySQL database with realistic historical records
from data/raw/synthetic_mess_data.csv for immediate dashboard visualization.
=============================================================================
"""

import csv
import sys
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.extensions import db
from app.models.mess_record import MessRecord, SurplusAdvisory, PredictionLog
from ml_engine.predict import get_predictor

CSV_PATH = BASE_DIR / "data" / "raw" / "synthetic_mess_data.csv"


def seed_database(limit_records: int = 180):
    """
    Seeds database with historical records (default: last 180 records = ~60 days)
    to provide realistic data for dashboard charts and analytics.
    """
    app = create_app()
    with app.app_context():
        # Check if database already has records
        existing_count = MessRecord.query.count()
        if existing_count >= limit_records:
            print(f"ℹ️ Database already contains {existing_count} records. Seeding skipped.")
            return

        print("=" * 60)
        print("🌱 Seeding Database with Historical Mess Records...")
        print("=" * 60)

        if not CSV_PATH.exists():
            print(f"❌ Synthetic CSV missing at {CSV_PATH}. Run ml_engine/generate_dataset.py first.")
            return

        records_to_insert = []
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)

        # Take the most recent rows up to limit_records
        selected_rows = all_rows[-limit_records:]

        for row in selected_rows:
            rec_date = datetime.strptime(row["record_date"], "%Y-%m-%d").date()
            prep = int(row["prepared_meals"])
            consumed = int(row["consumed_meals"])
            wasted = int(row["wasted_meals"])
            waste_pct = float(row["waste_percentage"])

            rec = MessRecord(
                record_date=rec_date,
                day_of_week=row["day_of_week"],
                meal_type=row["meal_type"],
                menu_name=row["menu_name"],
                attendance=int(row["attendance"]),
                prepared_meals=prep,
                consumed_meals=consumed,
                wasted_meals=wasted,
                waste_percentage=waste_pct,
                notes=f"Historical log for {row['menu_category']}"
            )
            records_to_insert.append(rec)

        db.session.bulk_save_objects(records_to_insert)
        db.session.commit()
        print(f"✅ Successfully inserted {len(records_to_insert)} mess records into database.")

        # Also create initial surplus advisories for records with noticeable surplus (> 25 meals)
        surplus_records = MessRecord.query.filter(MessRecord.wasted_meals >= 25).order_by(MessRecord.record_date.desc()).limit(15).all()
        for s_rec in surplus_records:
            exists = SurplusAdvisory.query.filter_by(record_id=s_rec.id).first()
            if not exists:
                advisory = SurplusAdvisory(
                    record_id=s_rec.id,
                    date=s_rec.record_date,
                    meal_type=s_rec.meal_type,
                    surplus_quantity=s_rec.wasted_meals,
                    status="Pending Review",
                    food_safety_verified=False,
                    advisory_notes=f"High surplus observed for {s_rec.menu_name}. Verify food temperature & hygiene before donation."
                )
                db.session.add(advisory)

        db.session.commit()
        print(f"✅ Created initial surplus advisories for {len(surplus_records)} high-surplus records.")


if __name__ == "__main__":
    seed_database()
