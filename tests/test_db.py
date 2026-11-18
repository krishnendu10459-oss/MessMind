"""
=============================================================================
Unit & Integration Tests: Database Models, Constraints & Password Encoding
File: tests/test_db.py
=============================================================================
"""

import os
from datetime import date
from urllib.parse import quote_plus
import pytest
from app import create_app
from app.config import Config, mask_connection_uri
from app.extensions import db
from app.models.mess_record import MessRecord, PredictionLog, SurplusAdvisory


class TestDBConfig:
    """Isolated In-Memory configuration for database unit tests."""
    SECRET_KEY = "test-secret"
    FLASK_ENV = "development"
    DEBUG = False
    TESTING = True
    IS_PRODUCTION = False
    ALLOW_SQLITE_FALLBACK = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ACTIVE_DB_TYPE = "sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    ML_MODEL_PATH = Config.ML_MODEL_PATH
    PREPROCESSOR_PATH = Config.PREPROCESSOR_PATH
    METRICS_PATH = Config.METRICS_PATH


@pytest.fixture
def app():
    app = create_app(TestDBConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_mess_record_creation_and_waste_calc(app):
    """Test adding a mess record and verifying waste calculations."""
    record = MessRecord(
        record_date=date(2026, 11, 14),
        day_of_week="Saturday",
        meal_type="Lunch",
        menu_name="Paneer Butter Masala",
        attendance=400,
        prepared_meals=450,
        consumed_meals=410,
        wasted_meals=0,
        waste_percentage=0.0
    )
    record.calculate_waste()

    assert record.wasted_meals == 40
    assert record.waste_percentage == round((40 / 450) * 100, 2)

    db.session.add(record)
    db.session.commit()

    queried = db.session.get(MessRecord, record.id)
    assert queried is not None
    assert queried.menu_name == "Paneer Butter Masala"
    assert queried.wasted_meals == 40


def test_prediction_log_storage(app):
    """Test storing AI predictions in database."""
    log = PredictionLog(
        prediction_date=date(2026, 11, 15),
        meal_type="Dinner",
        menu_name="Dal Tadka & Rice",
        expected_attendance=350,
        predicted_meals=320,
        confidence_interval_min=305,
        confidence_interval_max=335
    )
    db.session.add(log)
    db.session.commit()

    saved_log = PredictionLog.query.first()
    assert saved_log is not None
    assert saved_log.predicted_meals == 320


def test_surplus_advisory_status(app):
    """Test surplus advisory requiring human verification."""
    advisory = SurplusAdvisory(
        date=date(2026, 11, 14),
        meal_type="Lunch",
        surplus_quantity=35,
        status="Pending Review",
        food_safety_verified=False
    )
    db.session.add(advisory)
    db.session.commit()

    saved = SurplusAdvisory.query.first()
    assert saved is not None
    assert saved.status == "Pending Review"
    assert saved.food_safety_verified is False


def test_cascade_delete_mess_record_preserves_surplus_advisory(app):
    """Test that deleting a kitchen MessRecord sets SurplusAdvisory.record_id to NULL, preserving audit history."""
    record = MessRecord(
        record_date=date(2026, 11, 14),
        day_of_week="Saturday",
        meal_type="Lunch",
        menu_name="Chole Bhature",
        attendance=300,
        prepared_meals=350,
        consumed_meals=300,
        wasted_meals=50,
        waste_percentage=14.29
    )
    db.session.add(record)
    db.session.commit()

    advisory = SurplusAdvisory(
        record_id=record.id,
        date=date(2026, 11, 14),
        meal_type="Lunch",
        surplus_quantity=50,
        status="Pending Review",
        food_safety_verified=False,
        advisory_notes="Advisory audit trail linked to record."
    )
    db.session.add(advisory)
    db.session.commit()

    advisory_id = advisory.id
    # Delete the parent MessRecord
    db.session.delete(record)
    db.session.commit()
    db.session.expire_all()

    # Verify advisory record is NOT lost, but record_id became NULL
    preserved_adv = db.session.get(SurplusAdvisory, advisory_id)
    assert preserved_adv is not None
    assert preserved_adv.record_id is None
    assert preserved_adv.surplus_quantity == 50


def test_waste_calculation_boundary_enforcement():
    """Verify that calculate_waste safely enforces boundaries (no negative waste, percentage <= 100)."""
    rec = MessRecord(
        record_date=date(2026, 11, 14),
        day_of_week="Saturday",
        meal_type="Breakfast",
        menu_name="Idli Sambar",
        attendance=100,
        prepared_meals=0,
        consumed_meals=0,
        wasted_meals=0,
        waste_percentage=0.0
    )
    rec.calculate_waste()
    assert rec.wasted_meals == 0
    assert rec.waste_percentage == 0.0

    # Over-consumption edge case (prevent negative waste)
    rec.prepared_meals = 100
    rec.consumed_meals = 120
    rec.calculate_waste()
    assert rec.wasted_meals == 0


def test_workflow_step8_metrics_calculation():
    """
    Step 8 Unit Test: Verifies:
    - Actual food waste = Prepared meals - Consumed meals
    - Estimated surplus before preparation = Prepared meals planned - Predicted demand
    - Prediction error = Actual consumption - Predicted consumption
    - Does NOT calculate actual waste if consumed meals is None.
    """
    # Case A: Completed meal with AI prediction linkage
    rec_completed = MessRecord(
        record_date=date(2026, 11, 20),
        day_of_week="Friday",
        meal_type="Lunch",
        menu_name="Veg Biryani",
        attendance=500,
        prepared_meals=475,
        consumed_meals=450,
        predicted_meals=440
    )
    rec_completed.calculate_waste()
    assert rec_completed.wasted_meals == 25           # 475 - 450
    assert rec_completed.waste_percentage == round((25 / 475) * 100, 2)
    assert rec_completed.estimated_surplus == 35      # 475 - 440
    assert rec_completed.prediction_error == 10       # 450 - 440

    # Case B: Ongoing meal (consumed meals is None)
    rec_ongoing = MessRecord(
        record_date=date(2026, 11, 20),
        day_of_week="Friday",
        meal_type="Lunch",
        menu_name="Veg Biryani",
        attendance=500,
        prepared_meals=475,
        consumed_meals=None,
        predicted_meals=440
    )
    rec_ongoing.calculate_waste()
    assert rec_ongoing.wasted_meals is None           # Actual waste MUST NOT be calculated
    assert rec_ongoing.waste_percentage is None
    assert rec_ongoing.estimated_surplus == 35        # Planned cushion is known
    assert rec_ongoing.prediction_error is None       # Error cannot be known until consumed


def test_password_url_encoding_and_masking():
    """Verify passwords containing special characters (@, #, :, /, %, &) are safely URL-encoded and masked."""
    raw_passwords = [
        "P@ssw0rd!#123",
        "secret:pass/with@symbols%",
        "c0mpl&x?p@ss=word",
    ]

    for raw_pw in raw_passwords:
        encoded_pw = quote_plus(raw_pw)
        # Verify reserved delimiters @, :, / are replaced
        assert "@" not in encoded_pw
        assert ":" not in encoded_pw
        assert "/" not in encoded_pw

        # Construct URI and verify masking
        uri = f"mysql+pymysql://admin:{encoded_pw}@db.college.edu:3306/food_waste_db"
        masked = mask_connection_uri(uri)
        assert raw_pw not in masked
        assert encoded_pw not in masked
        assert ":****@" in masked
        assert "db.college.edu:3306/food_waste_db" in masked
