"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: app/models/mess_record.py
Description: SQLAlchemy ORM Data Models for Mess Records, Prediction Logs,
and Surplus Food Donation Advisories with full workflow integration metrics.
=============================================================================
"""

from datetime import datetime, timezone
from app.extensions import db


def get_utc_now():
    """Returns current UTC timestamp in a Python 3.14+ compliant manner."""
    return datetime.now(timezone.utc)


class MessRecord(db.Model):
    """Daily record of prepared meals, actual attendance, consumption, and prediction integration."""
    __tablename__ = "mess_records"
    __table_args__ = (
        db.CheckConstraint("prepared_meals >= 0", name="chk_prepared_positive"),
        db.CheckConstraint("attendance >= 0", name="chk_attendance_nonneg"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    day_of_week = db.Column(db.String(20), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False, index=True)
    menu_name = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.Integer, nullable=False)
    prepared_meals = db.Column(db.Integer, nullable=False)
    consumed_meals = db.Column(db.Integer, nullable=True)  # Nullable: None if meal is currently ongoing
    wasted_meals = db.Column(db.Integer, nullable=True)    # Nullable: Calculated only when consumed_meals is known
    waste_percentage = db.Column(db.Float, nullable=True)   # Nullable: Calculated only when consumed_meals is known
    
    # Workflow Integration Columns:
    predicted_meals = db.Column(db.Integer, nullable=True)   # AI Predicted Demand from ML model
    estimated_surplus = db.Column(db.Integer, nullable=True) # Planned prep - predicted demand
    prediction_error = db.Column(db.Integer, nullable=True)  # Actual consumption - predicted demand
    
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def calculate_waste(self):
        """
        Computes actual food waste, planned surplus, and prediction error.
        Guarantees that actual waste is NOT computed before actual consumption is known.
        """
        # 1. Actual food waste = Prepared meals - Consumed meals (only if consumed is recorded)
        if self.consumed_meals is not None and self.prepared_meals is not None:
            self.wasted_meals = max(0, self.prepared_meals - self.consumed_meals)
            if self.prepared_meals > 0:
                pct = (self.wasted_meals / self.prepared_meals) * 100
                self.waste_percentage = round(min(100.0, max(0.0, pct)), 2)
            else:
                self.waste_percentage = 0.0
        else:
            self.wasted_meals = None
            self.waste_percentage = None

        # 2. Estimated surplus before prep = Planned prep - Predicted demand
        if self.prepared_meals is not None and self.predicted_meals is not None:
            self.estimated_surplus = self.prepared_meals - self.predicted_meals
        else:
            self.estimated_surplus = None

        # 3. Prediction error = Actual consumption - Predicted consumption
        if self.consumed_meals is not None and self.predicted_meals is not None:
            self.prediction_error = self.consumed_meals - self.predicted_meals
        else:
            self.prediction_error = None

    def to_dict(self):
        return {
            "id": self.id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "day_of_week": self.day_of_week,
            "meal_type": self.meal_type,
            "menu_name": self.menu_name,
            "attendance": self.attendance,
            "prepared_meals": self.prepared_meals,
            "consumed_meals": self.consumed_meals,
            "wasted_meals": self.wasted_meals,
            "waste_percentage": self.waste_percentage,
            "predicted_meals": self.predicted_meals,
            "estimated_surplus": self.estimated_surplus,
            "prediction_error": self.prediction_error,
            "notes": self.notes
        }


class PredictionLog(db.Model):
    """Log of ML model predictions made for meal planning."""
    __tablename__ = "prediction_logs"
    __table_args__ = (
        db.CheckConstraint("predicted_meals >= 0", name="chk_predicted_positive"),
        db.CheckConstraint("expected_attendance >= 0", name="chk_attendance_positive"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prediction_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    menu_name = db.Column(db.String(100), nullable=False)
    expected_attendance = db.Column(db.Integer, nullable=False)
    predicted_meals = db.Column(db.Integer, nullable=False)
    confidence_interval_min = db.Column(db.Integer, nullable=True)
    confidence_interval_max = db.Column(db.Integer, nullable=True)
    model_version = db.Column(db.String(50), default="RandomForestRegressor_v1.0")
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "prediction_date": self.prediction_date.isoformat() if self.prediction_date else None,
            "meal_type": self.meal_type,
            "menu_name": self.menu_name,
            "expected_attendance": self.expected_attendance,
            "predicted_meals": self.predicted_meals,
            "confidence_interval_min": self.confidence_interval_min,
            "confidence_interval_max": self.confidence_interval_max,
            "model_version": self.model_version
        }


class SurplusAdvisory(db.Model):
    """Advisory records for potential surplus food donation requiring human verification."""
    __tablename__ = "surplus_advisories"
    __table_args__ = (
        db.CheckConstraint("surplus_quantity >= 0", name="chk_surplus_positive"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Foreign key with ON DELETE SET NULL to preserve donation records even if a kitchen log is purged
    record_id = db.Column(db.Integer, db.ForeignKey("mess_records.id", ondelete="SET NULL"), nullable=True)
    record = db.relationship("MessRecord", backref=db.backref("surplus_advisories", lazy="dynamic"))
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    surplus_quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Pending Review")
    food_safety_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(100), nullable=True)
    recipient_organization = db.Column(db.String(150), nullable=True)
    advisory_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "record_id": self.record_id,
            "date": self.date.isoformat() if self.date else None,
            "meal_type": self.meal_type,
            "surplus_quantity": self.surplus_quantity,
            "status": self.status,
            "food_safety_verified": self.food_safety_verified,
            "verified_by": self.verified_by,
            "recipient_organization": self.recipient_organization,
            "advisory_notes": self.advisory_notes
        }
