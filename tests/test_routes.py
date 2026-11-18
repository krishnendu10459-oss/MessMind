"""
=============================================================================
Unit & Integration Tests: Flask Routes, Health Monitoring, & DB Governance
File: tests/test_routes.py
=============================================================================
"""

import os
from datetime import date
from pathlib import Path
import pytest
from app import create_app
from app.config import Config, BASE_DIR
from app.extensions import db
from app.models.mess_record import MessRecord, PredictionLog, SurplusAdvisory


class TestRoutesConfig:
    """Isolated In-Memory configuration for route and integration testing."""
    SECRET_KEY = "test-routes-secret"
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
def client():
    app = create_app(TestRoutesConfig)
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        # Seed an initial baseline record
        rec = MessRecord(
            record_date=date(2026, 11, 14),
            day_of_week="Saturday",
            meal_type="Lunch",
            menu_name="Paneer Butter Masala & Naan",
            attendance=400,
            prepared_meals=450,
            consumed_meals=410,
            wasted_meals=40,
            waste_percentage=8.89,
            notes="Initial test record",
        )
        db.session.add(rec)
        db.session.commit()

        adv = SurplusAdvisory(
            record_id=rec.id,
            date=date(2026, 11, 14),
            meal_type="Lunch",
            surplus_quantity=40,
            status="Pending Review",
            food_safety_verified=False,
            recipient_organization="Robin Hood Army",
        )
        db.session.add(adv)
        db.session.commit()

        with app.test_client() as client:
            yield client
            db.session.remove()
            db.drop_all()


def test_root_redirects_to_dashboard(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"College Mess Operations Dashboard" in response.data
    assert b"Total Meals Prepared" in response.data
    assert b"consumptionChart" in response.data


def test_entry_page_get_and_post(client):
    # GET
    res_get = client.get("/entry")
    assert res_get.status_code == 200
    assert b"Record Mess Consumption" in res_get.data

    # POST valid
    post_data = {
        "record_date": "2026-11-15",
        "meal_type": "Dinner",
        "attendance": "400",
        "menu_name": "Paneer Butter Masala & Naan",
        "prepared_meals": "430",
        "consumed_meals": "395",
        "notes": "Test integration meal log",
    }
    res_post = client.post("/entry", data=post_data, follow_redirects=True)
    assert res_post.status_code == 200
    assert b"recorded successfully" in res_post.data or b"flagged for safety review" in res_post.data


def test_entry_validation_error(client):
    # Consumed > Prepared violation
    invalid_data = {
        "record_date": "2026-11-15",
        "meal_type": "Lunch",
        "attendance": "400",
        "menu_name": "Test Menu",
        "prepared_meals": "300",
        "consumed_meals": "400",  # Invalid!
    }
    res = client.post("/entry", data=invalid_data)
    assert res.status_code == 200
    assert b"Consumed meals cannot exceed prepared meals" in res.data


def test_edit_record_get_and_post(client):
    # Get a record to edit
    rec = MessRecord.query.first()
    assert rec is not None, "At least one record should exist to test edit."

    # GET edit page
    res_get = client.get(f"/records/edit/{rec.id}")
    assert res_get.status_code == 200
    assert f"Edit Mess Record #{rec.id}".encode() in res_get.data

    # POST edit update
    updated_data = {
        "record_date": rec.record_date.strftime("%Y-%m-%d"),
        "meal_type": rec.meal_type,
        "attendance": "420",
        "menu_name": "Updated Menu Item",
        "prepared_meals": "450",
        "consumed_meals": "410",
        "notes": "Updated by automated test",
    }
    res_post = client.post(f"/records/edit/{rec.id}", data=updated_data, follow_redirects=True)
    assert res_post.status_code == 200
    assert f"Record #{rec.id} updated successfully!".encode() in res_post.data

    # Verify database update
    updated_rec = db.session.get(MessRecord, rec.id)
    assert updated_rec.menu_name == "Updated Menu Item"
    assert updated_rec.attendance == 420
    assert updated_rec.wasted_meals == 40


def test_predict_page_get_and_post(client):
    # GET
    res_get = client.get("/predict")
    assert res_get.status_code == 200
    assert b"AI Meal Demand Predictor" in res_get.data

    # POST prediction
    pred_data = {
        "pred_date": "2026-11-20",
        "pred_meal": "Lunch",
        "pred_menu": "Veg Biryani & Mirchi Ka Salan",
        "pred_attendance": "500",
    }
    res_post = client.post("/predict", data=pred_data)
    assert res_post.status_code == 200
    assert b"Predicted Consumption" in res_post.data
    assert b"Recommended Preparation" in res_post.data
    assert b"Estimated Demand Range" in res_post.data


def test_analytics_page(client):
    res = client.get("/analytics")
    assert res.status_code == 200
    assert b"Food Waste Analytics" in res.data
    assert b"menuWasteChart" in res.data


def test_records_page_and_filtering(client):
    res = client.get("/records")
    assert res.status_code == 200
    assert b"Previous Mess Consumption Logs" in res.data

    # Search filter
    res_search = client.get("/records?q=Biryani")
    assert res_search.status_code == 200


def test_surplus_page_and_update(client):
    res = client.get("/surplus")
    assert res.status_code == 200
    assert b"Surplus Food Advisory" in res.data
    assert b"Robin Hood Army" in res.data

    # Test updating a surplus advisory
    adv = SurplusAdvisory.query.first()
    if adv:
        update_data = {
            "advisory_id": str(adv.id),
            "status": "Safe for Donation",
            "verified_by": "Test Supervisor",
            "recipient_organization": "Robin Hood Army",
        }
        res_post = client.post("/surplus/update", data=update_data, follow_redirects=True)
        assert res_post.status_code == 200
        assert b"Safe for Donation" in res_post.data


def test_api_chart_data(client):
    res = client.get("/api/chart-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "dates" in data
    assert "prepared" in data
    assert "consumed" in data


def test_api_analytics_charts(client):
    res = client.get("/api/analytics-charts")
    assert res.status_code == 200
    data = res.get_json()
    assert "menu_analysis" in data
    assert "meal_distribution" in data
    assert "trend" in data


def test_api_export_csv(client):
    res = client.get("/api/export-csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["Content-Type"]
    assert "attachment" in res.headers["Content-Disposition"]
    assert b"Record ID,Date,Day of Week" in res.data


def test_api_health_endpoint(client):
    """Test /api/health and /api/status endpoint response structure and diagnostic data."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert data["database"]["connected"] is True
    assert data["database"]["active_type"] in ("sqlite", "mysql")
    assert "masked_target" in data["database"]
    assert "records" in data
    assert data["records"]["mess_records"] > 0


def test_mysql_unreachable_fails_when_fallback_disabled():
    """Verify that when ALLOW_SQLITE_FALLBACK=False (default), unreachable MySQL aborts startup."""
    class FakeMySQLStrictConfig:
        SECRET_KEY = "test"
        FLASK_ENV = "development"
        DEBUG = True
        IS_PRODUCTION = False
        ALLOW_SQLITE_FALLBACK = False  # Strict failover policy
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://invalid_user:invalid_pass@127.0.0.1:3306/invalid_db"
        ACTIVE_DB_TYPE = "mysql"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "connect_args": {"connect_timeout": 1}}
        ML_MODEL_PATH = None
        PREPROCESSOR_PATH = None
        METRICS_PATH = None

    with pytest.raises(RuntimeError) as exc_info:
        create_app(FakeMySQLStrictConfig)

    assert "ALLOW_SQLITE_FALLBACK=false" in str(exc_info.value) or "Failed to connect to MySQL" in str(exc_info.value)


def test_mysql_unreachable_controlled_fallback_in_development():
    """Verify that when ALLOW_SQLITE_FALLBACK=True in development, application falls back to SQLite."""
    class FakeMySQLControlledFallbackConfig:
        SECRET_KEY = "test"
        FLASK_ENV = "development"
        DEBUG = True
        IS_PRODUCTION = False
        ALLOW_SQLITE_FALLBACK = True  # Explicitly permitted fallback
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://invalid_user:invalid_pass@127.0.0.1:3306/invalid_db"
        ACTIVE_DB_TYPE = "mysql"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "connect_args": {"connect_timeout": 1}}
        ML_MODEL_PATH = None
        PREPROCESSOR_PATH = None
        METRICS_PATH = None

    fallback_app = create_app(FakeMySQLControlledFallbackConfig)
    assert fallback_app.config["ACTIVE_DB_TYPE"] == "sqlite"
    assert fallback_app.config["DB_FALLBACK_ACTIVE"] is True
    assert fallback_app.config["DB_STATUS"] == "degraded"
    assert "sqlite" in fallback_app.config["SQLALCHEMY_DATABASE_URI"]

    with fallback_app.app_context():
        # SQLite queries work properly in controlled fallback mode
        count = MessRecord.query.count()
        assert count >= 0


def test_mysql_unreachable_in_production_never_falls_back():
    """Verify that in production mode, fallback is strictly prohibited even if ALLOW_SQLITE_FALLBACK=True."""
    class FakeMySQLProductionConfig:
        SECRET_KEY = "test"
        FLASK_ENV = "production"
        DEBUG = False
        IS_PRODUCTION = True
        ALLOW_SQLITE_FALLBACK = True  # Forbidden in production!
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://prod_user:prod_pass@127.0.0.1:3306/prod_food_waste_db"
        ACTIVE_DB_TYPE = "mysql"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "connect_args": {"connect_timeout": 1}}
        ML_MODEL_PATH = None
        PREPROCESSOR_PATH = None
        METRICS_PATH = None

    with pytest.raises(RuntimeError) as exc_info:
        create_app(FakeMySQLProductionConfig)

    assert "Production startup aborted" in str(exc_info.value) or "strictly prohibited in production" in str(exc_info.value)


def test_records_persist_across_app_restart():
    """Verify that restarting the application retains previously saved database records."""
    test_db_file = BASE_DIR / "database" / "test_restart_persistence.db"
    test_db_file.parent.mkdir(parents=True, exist_ok=True)
    if test_db_file.exists():
        test_db_file.unlink()

    class PersistentTestConfig:
        SECRET_KEY = "test-persistent"
        FLASK_ENV = "development"
        DEBUG = False
        TESTING = True
        IS_PRODUCTION = False
        ALLOW_SQLITE_FALLBACK = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{test_db_file.as_posix()}"
        ACTIVE_DB_TYPE = "sqlite"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
        ML_MODEL_PATH = Config.ML_MODEL_PATH
        PREPROCESSOR_PATH = Config.PREPROCESSOR_PATH
        METRICS_PATH = Config.METRICS_PATH

    # App instance 1: insert records
    app1 = create_app(PersistentTestConfig)
    with app1.app_context():
        rec = MessRecord(
            record_date=date(2026, 11, 20),
            day_of_week="Friday",
            meal_type="Dinner",
            menu_name="Dal Tadka & Rice",
            attendance=350,
            prepared_meals=380,
            consumed_meals=340,
            wasted_meals=40,
            waste_percentage=10.53,
            notes="Persistence verification record"
        )
        db.session.add(rec)
        db.session.commit()
        count1 = MessRecord.query.count()

    # App instance 2: simulating complete process restart with fresh context
    app2 = create_app(PersistentTestConfig)
    with app2.app_context():
        count2 = MessRecord.query.count()
        persisted_rec = MessRecord.query.filter_by(notes="Persistence verification record").first()
        assert persisted_rec is not None
        assert persisted_rec.prepared_meals == 380

    assert count1 == count2
    assert count2 > 0

    # Cleanup temporary test file
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except Exception:
            pass


# =============================================================================
# PHASE 4 COMPLETE WORKFLOW INTEGRATION TESTS
# =============================================================================

def test_complete_phase4_end_to_end_workflow(client):
    """
    Verifies the complete 10-step workflow:
    1. Dashboard opens.
    2-6. Prediction generated and displayed.
    7-8. Planned prep and actual consumption recorded, calculating:
         - Actual Food Waste = Prepared - Consumed
         - Estimated Planned Surplus = Prepared - Predicted
         - Prediction Error = Consumed - Predicted
    9. Database saves both record and prediction log.
    10. Dashboard and analytics update.
    """
    # Step 1: Open Dashboard
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200

    # Steps 2-5: Generate AI Prediction
    pred_payload = {
        "pred_date": "2026-11-25",
        "pred_meal": "Lunch",
        "pred_attendance": "500",
        "pred_menu": "Veg Biryani & Mirchi Ka Salan",
    }
    res_pred = client.post("/predict", data=pred_payload)
    assert res_pred.status_code == 200
    assert b"AI Analysis Complete" in res_pred.data
    assert b"Recommended Preparation" in res_pred.data

    # Step 6: Verify prediction was saved in prediction_logs
    latest_log = PredictionLog.query.filter_by(menu_name="Veg Biryani & Mirchi Ka Salan").order_by(PredictionLog.id.desc()).first()
    assert latest_log is not None
    predicted_val = latest_log.predicted_meals
    assert predicted_val > 0

    # Steps 7-9: Daily Data Entry after meal dining completes
    # Planned prep = 470, actual consumed = 450, predicted demand = predicted_val
    entry_payload = {
        "record_date": "2026-11-25",
        "meal_type": "Lunch",
        "attendance": "500",
        "menu_name": "Veg Biryani & Mirchi Ka Salan",
        "prepared_meals": "470",
        "consumed_meals": "450",
        "predicted_meals": str(predicted_val),
        "notes": "Phase 4 End-to-end integration test record",
    }
    res_entry = client.post("/entry", data=entry_payload, follow_redirects=True)
    assert res_entry.status_code == 200
    assert b"Mess log for Veg Biryani" in res_entry.data or b"flagged for safety review" in res_entry.data

    # Step 8 Verification: Check the calculations in saved database record
    saved_rec = MessRecord.query.filter_by(notes="Phase 4 End-to-end integration test record").first()
    assert saved_rec is not None
    # 1. Actual food waste = Prepared meals - Consumed meals
    assert saved_rec.wasted_meals == (470 - 450)  # 20 meals
    assert saved_rec.waste_percentage == round((20 / 470) * 100, 2)
    # 2. Estimated surplus before prep = Prepared meals planned - Predicted demand
    assert saved_rec.estimated_surplus == (470 - predicted_val)
    # 3. Prediction error = Actual consumption - Predicted consumption
    assert saved_rec.prediction_error == (450 - predicted_val)

    # Step 10: Dashboard updates with the saved record
    res_updated_dash = client.get("/dashboard")
    assert res_updated_dash.status_code == 200
    assert b"Phase 4 End-to-end" in res_updated_dash.data or b"Veg Biryani" in res_updated_dash.data


def test_in_progress_meal_workflow_no_premature_waste(client):
    """
    Verifies that if actual consumption is not yet known:
    - Consumed meals is None.
    - Actual waste is NOT calculated prematurely.
    - Planned surplus before preparation is still calculated if prediction was linked.
    - Operator later edits the record to log actual consumption, triggering waste calculation.
    """
    # 1. Save meal while cooking is done but dining is ongoing (no consumed meals)
    ongoing_payload = {
        "record_date": "2026-11-26",
        "meal_type": "Dinner",
        "attendance": "400",
        "menu_name": "Dal Makhani & Roti/Rice",
        "prepared_meals": "420",
        "consumed_meals": "",  # Empty: dining in progress!
        "predicted_meals": "395",
        "notes": "Ongoing dining test",
    }
    res_save = client.post("/entry", data=ongoing_payload, follow_redirects=True)
    assert res_save.status_code == 200
    assert b"saved as Ongoing" in res_save.data or b"recorded successfully" in res_save.data

    rec = MessRecord.query.filter_by(notes="Ongoing dining test").first()
    assert rec is not None
    assert rec.consumed_meals is None
    assert rec.wasted_meals is None  # MUST NOT compute waste before consumption!
    assert rec.waste_percentage is None
    assert rec.estimated_surplus == (420 - 395)  # 25 meals planned safety cushion
    assert rec.prediction_error is None  # Error cannot be known before consumption

    # 2. Dining completes: operator edits record to log 405 consumed meals
    edit_payload = {
        "record_date": "2026-11-26",
        "meal_type": "Dinner",
        "attendance": "400",
        "menu_name": "Dal Makhani & Roti/Rice",
        "prepared_meals": "420",
        "consumed_meals": "405",  # Entered after dining
        "predicted_meals": "395",
        "notes": "Completed dining test",
    }
    res_edit = client.post(f"/records/edit/{rec.id}", data=edit_payload, follow_redirects=True)
    assert res_edit.status_code == 200

    updated = db.session.get(MessRecord, rec.id)
    assert updated.consumed_meals == 405
    assert updated.wasted_meals == (420 - 405)  # 15 meals actual waste
    assert updated.waste_percentage == round((15 / 420) * 100, 2)
    assert updated.estimated_surplus == (420 - 395)  # 25 meals
    assert updated.prediction_error == (405 - 395)  # +10 meals error


def test_empty_state_handling():
    """Verify that when 0 records exist, dashboard, analytics, and records display suitable empty states without crashes."""
    class EmptyDBConfig:
        SECRET_KEY = "test"
        FLASK_ENV = "development"
        DEBUG = True
        IS_PRODUCTION = False
        ALLOW_SQLITE_FALLBACK = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Completely empty fresh database
        ACTIVE_DB_TYPE = "sqlite"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
        ML_MODEL_PATH = None
        PREPROCESSOR_PATH = None
        METRICS_PATH = None

    empty_app = create_app(EmptyDBConfig)
    empty_app.config["TESTING"] = True
    with empty_app.test_client() as empty_client:
        # Dashboard empty state
        dash_res = empty_client.get("/dashboard")
        assert dash_res.status_code == 200
        assert b"No Mess Records Yet" in dash_res.data

        # Analytics empty state
        analytics_res = empty_client.get("/analytics")
        assert analytics_res.status_code == 200
        assert b"No Completed Meal Records for Analytics" in analytics_res.data

        # Records empty state
        records_res = empty_client.get("/records")
        assert records_res.status_code == 200
        assert b"No Records Found" in records_res.data


def test_csrf_token_enforcement():
    """Verify CSRF middleware blocks requests without a valid CSRF token when enabled."""
    class CSRFActiveConfig(TestRoutesConfig):
        TESTING = True
        WTF_CSRF_ENABLED = True

    csrf_app = create_app(CSRFActiveConfig)
    csrf_app.config["TESTING"] = True
    csrf_app.config["WTF_CSRF_ENABLED"] = True

    with csrf_app.test_client() as csrf_client:
        # 1. POST without token is blocked with 403 Forbidden
        blocked_res = csrf_client.post("/entry", data={
            "record_date": "2026-11-28",
            "meal_type": "Lunch",
            "menu_name": "Veg Pulav",
            "attendance": "300",
            "prepared_meals": "320",
        })
        assert blocked_res.status_code == 403
        assert b"CSRF token missing or invalid" in blocked_res.data

        # 2. POST with valid session token is accepted
        with csrf_client.session_transaction() as sess:
            sess["_csrf_token"] = "valid-test-csrf-token-xyz"

        allowed_res = csrf_client.post("/entry", data={
            "csrf_token": "valid-test-csrf-token-xyz",
            "record_date": "2026-11-28",
            "meal_type": "Lunch",
            "menu_name": "Veg Pulav",
            "attendance": "300",
            "prepared_meals": "320",
            "consumed_meals": "290",
        }, follow_redirects=True)
        assert allowed_res.status_code == 200
        assert b"saved!" in allowed_res.data or b"recorded successfully" in allowed_res.data


def test_negative_consumption_validation(client):
    """Verify that negative consumed meals values are strictly rejected."""
    payload = {
        "record_date": "2026-11-29",
        "meal_type": "Dinner",
        "menu_name": "Rajma Masala & Rice",
        "attendance": "350",
        "prepared_meals": "380",
        "consumed_meals": "-15",
    }
    response = client.post("/entry", data=payload)
    assert response.status_code == 200
    assert b"Consumed meals cannot be negative" in response.data

    # Ensure record was NOT created in DB
    rec = MessRecord.query.filter_by(record_date=date(2026, 11, 29)).first()
    assert rec is None


def test_boundary_attendance_and_prepared(client):
    """Verify input boundary enforcement for attendance and prepared meals."""
    # Attendance <= 0
    res_zero = client.post("/entry", data={
        "record_date": "2026-11-29",
        "meal_type": "Breakfast",
        "menu_name": "Idli Sambar",
        "attendance": "0",
        "prepared_meals": "100",
    })
    assert res_zero.status_code == 200
    assert b"must be greater than zero" in res_zero.data

    # Prepared <= 0
    res_zero_prep = client.post("/entry", data={
        "record_date": "2026-11-29",
        "meal_type": "Breakfast",
        "menu_name": "Idli Sambar",
        "attendance": "100",
        "prepared_meals": "0",
    })
    assert res_zero_prep.status_code == 200
    assert b"must be greater than zero" in res_zero_prep.data

    # Consumed == 0 (Valid zero consumption, e.g. cancelled event or 100% waste)
    res_zero_cons = client.post("/entry", data={
        "record_date": "2026-11-30",
        "meal_type": "Breakfast",
        "menu_name": "Poha",
        "attendance": "100",
        "prepared_meals": "100",
        "consumed_meals": "0",
    }, follow_redirects=True)
    assert res_zero_cons.status_code == 200
    rec_zero = MessRecord.query.filter_by(record_date=date(2026, 11, 30)).first()
    assert rec_zero is not None
    assert rec_zero.consumed_meals == 0
    assert rec_zero.wasted_meals == 100
    assert rec_zero.waste_percentage == 100.0

    # Attendance > 5000
    res_huge = client.post("/entry", data={
        "record_date": "2026-11-29",
        "meal_type": "Breakfast",
        "menu_name": "Idli Sambar",
        "attendance": "5500",
        "prepared_meals": "100",
    })
    assert res_huge.status_code == 200
    assert b"exceed standard hostel limits" in res_huge.data

    # Consumed > Prepared
    res_over = client.post("/entry", data={
        "record_date": "2026-11-29",
        "meal_type": "Breakfast",
        "menu_name": "Idli Sambar",
        "attendance": "100",
        "prepared_meals": "100",
        "consumed_meals": "150",
    })
    assert res_over.status_code == 200
    assert b"Consumed meals cannot exceed prepared meals" in res_over.data


def test_duplicate_entry_redirects_to_edit(client):
    """Verify that submitting a duplicate meal session redirects to the edit page."""
    # Baseline record exists for 2026-11-14 Lunch
    dup_payload = {
        "record_date": "2026-11-14",
        "meal_type": "Lunch",
        "menu_name": "Paneer Butter Masala",
        "attendance": "420",
        "prepared_meals": "460",
    }
    res = client.post("/entry", data=dup_payload, follow_redirects=True)
    assert res.status_code == 200
    assert b"Duplicate Notice" in res.data
    assert b"Redirected to edit page" in res.data


def test_records_pagination_page_controls(client):
    """Verify that records pagination breaks large datasets into 20-item pages."""
    # Seed 25 additional distinct records
    for i in range(1, 26):
        r = MessRecord(
            record_date=date(2026, 10, i),
            day_of_week="Monday",
            meal_type="Lunch" if i % 2 == 0 else "Dinner",
            menu_name=f"Paginated Menu {i}",
            attendance=300 + i,
            prepared_meals=320 + i,
            consumed_meals=310 + i,
            wasted_meals=10,
            waste_percentage=3.12,
        )
        db.session.add(r)
    db.session.commit()

    # Page 1
    p1 = client.get("/records?page=1")
    assert p1.status_code == 200
    assert b"Page <strong>1</strong> of <strong>2</strong>" in p1.data
    assert b"Next" in p1.data

    # Page 2
    p2 = client.get("/records?page=2")
    assert p2.status_code == 200
    assert b"Page <strong>2</strong> of <strong>2</strong>" in p2.data
    assert b"Previous" in p2.data


def test_custom_error_handlers(client):
    """Verify custom error page rendering and absence of stack trace exposure."""
    res_404 = client.get("/non-existent-audit-endpoint-404")
    assert res_404.status_code == 404
    assert b"Page Not Found" in res_404.data
    assert b"404" in res_404.data
    assert b"Traceback (most recent call last)" not in res_404.data


def test_health_endpoint_masks_absolute_filesystem_paths(client):
    """Verify /api/health sanitizes internal OS filesystem paths."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ("healthy", "degraded")
    uri = data["database"]["masked_target"]
    assert "Users" not in uri
    assert "LOQ" not in uri
    assert "Desktop" not in uri
