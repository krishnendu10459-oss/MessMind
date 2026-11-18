"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: database/init_db.py
Description: Standalone CLI database initialization script for SQLite/MySQL.
Ensures non-destructive table creation and optional seed data population.
=============================================================================
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text
from app import create_app
from app.config import Config
from app.extensions import db
from app.models.mess_record import MessRecord, PredictionLog, SurplusAdvisory
from database.seed_data import seed_database


def init_database(seed: bool = False):
    print("=" * 65)
    print("🛠️ DATABASE INITIALIZATION UTILITY")
    print("=" * 65)

    info = Config.get_db_info()
    print(f"Target Database Type : {info['active_type'].upper()}")
    print(f"Connection Target    : {info['uri_masked']}")
    print("-" * 65)

    app = create_app()
    with app.app_context():
        try:
            # 1. Connection check
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Connection check passed!")

            # 2. Non-destructive table creation
            db.create_all()
            print("✅ Schema verification: All tables (mess_records, prediction_logs, surplus_advisories) exist.")

            # 3. Existing record audit
            record_count = MessRecord.query.count()
            prediction_count = PredictionLog.query.count()
            advisory_count = SurplusAdvisory.query.count()

            print(f"📊 Current Database Counts:")
            print(f"   • Mess Daily Records : {record_count}")
            print(f"   • Prediction Logs    : {prediction_count}")
            print(f"   • Surplus Advisories : {advisory_count}")

            # 4. Optional seeding
            if seed:
                print("\n🌱 Seeding requested...")
                seed_database(limit_records=180)
            elif record_count == 0:
                print("\nℹ️ Database is empty. Seeding with sample data for demonstration...")
                seed_database(limit_records=180)

            print("-" * 65)
            print("🎉 Database is ready for operations!")
            print("=" * 65)

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Food Waste Prediction Database.")
    parser.add_argument("--seed", action="store_true", help="Force populate database with sample records")
    args = parser.parse_args()
    init_database(seed=args.seed)
