"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: app/routes/api_routes.py
Description: JSON API endpoints for Chart.js, CSV reporting, and System Health/Diagnostic monitoring.
=============================================================================
"""

import csv
import io
from flask import Blueprint, jsonify, request, Response, current_app
from sqlalchemy import func, text

from app.config import Config
from app.extensions import db
from app.models.mess_record import MessRecord, PredictionLog, SurplusAdvisory
from ml_engine.predict import get_predictor

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health")
@api_bp.route("/status")
def health_check():
    """Diagnostic health check verifying application and database connectivity."""
    active_type = current_app.config.get("ACTIVE_DB_TYPE", "sqlite")
    is_fallback = current_app.config.get("DB_FALLBACK_ACTIVE", False)
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    masked_target = Config.get_masked_uri(uri)
    is_prod = current_app.config.get("IS_PRODUCTION", False)
    allow_fallback = current_app.config.get("ALLOW_SQLITE_FALLBACK", False)

    # Live database connection ping
    connected = False
    error_msg = None
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        connected = True
    except Exception as e:
        error_msg = str(e)

    # Query record counts if connected
    record_count = 0
    prediction_count = 0
    advisory_count = 0
    if connected:
        try:
            record_count = MessRecord.query.count()
            prediction_count = PredictionLog.query.count()
            advisory_count = SurplusAdvisory.query.count()
        except Exception as e:
            error_msg = f"Table query error: {str(e)}"

    if not connected:
        overall_status = "unhealthy"
        status_code = 503
    elif is_fallback:
        overall_status = "degraded"
        status_code = 200
    else:
        overall_status = "healthy"
        status_code = 200

    return jsonify({
        "status": overall_status,
        "database": {
            "active_type": active_type,
            "connected": connected,
            "masked_target": masked_target,
            "fallback_active": is_fallback,
            "allow_fallback_configured": allow_fallback,
        },
        "records": {
            "mess_records": record_count,
            "prediction_logs": prediction_count,
            "surplus_advisories": advisory_count,
        },
        "environment": "production" if is_prod else "development",
        "error": error_msg,
    }), status_code


@api_bp.route("/chart-data")
def chart_data():
    """
    Returns recent completed records for dashboard Chart.js graphs.
    Filters out in-progress meals where actual consumption has not occurred yet.
    """
    records = (
        MessRecord.query.filter(MessRecord.consumed_meals.isnot(None))
        .order_by(MessRecord.record_date.desc(), MessRecord.id.desc())
        .limit(14)
        .all()
    )
    # Reverse to chronological order for line/bar visualization
    records = list(reversed(records))

    dates = [f"{r.record_date.strftime('%d %b')} ({r.meal_type[:1]})" for r in records]
    prepared = [r.prepared_meals for r in records]
    consumed = [r.consumed_meals for r in records]
    wasted = [r.wasted_meals for r in records]
    waste_percentages = [r.waste_percentage for r in records]

    return jsonify({
        "dates": dates,
        "prepared": prepared,
        "consumed": consumed,
        "wasted": wasted,
        "waste_percentages": waste_percentages,
    })


@api_bp.route("/analytics-charts")
def analytics_charts():
    """
    Returns aggregated data for analytics visualizations based on verified completed meals.
    """
    # 1. Menu-wise average waste ranking (Top 8 menus)
    menu_stats = (
        db.session.query(
            MessRecord.menu_name,
            func.avg(MessRecord.wasted_meals).label("avg_waste"),
            func.count(MessRecord.id).label("occurrences")
        )
        .filter(MessRecord.wasted_meals.isnot(None))
        .group_by(MessRecord.menu_name)
        .order_by(func.avg(MessRecord.wasted_meals).desc())
        .limit(8)
        .all()
    )

    menus = [m[0][:24] + ("..." if len(m[0]) > 24 else "") for m in menu_stats]
    avg_wastes = [round(float(m[1]), 1) for m in menu_stats]

    # 2. Waste by meal session (Breakfast vs Lunch vs Dinner)
    session_stats = (
        db.session.query(
            MessRecord.meal_type,
            func.sum(MessRecord.wasted_meals).label("session_waste")
        )
        .filter(MessRecord.wasted_meals.isnot(None))
        .group_by(MessRecord.meal_type)
        .all()
    )

    session_labels = [s[0] for s in session_stats]
    session_values = [int(s[1] or 0) for s in session_stats]

    # 3. Last 30 completed records waste trend
    recent_30 = (
        MessRecord.query.filter(MessRecord.wasted_meals.isnot(None))
        .order_by(MessRecord.record_date.desc(), MessRecord.id.desc())
        .limit(30)
        .all()
    )
    recent_30 = list(reversed(recent_30))
    trend_dates = [f"{r.record_date.strftime('%d %b')}" for r in recent_30]
    trend_wastes = [r.wasted_meals for r in recent_30]

    return jsonify({
        "menu_analysis": {
            "menus": menus,
            "avg_wastes": avg_wastes,
        },
        "meal_distribution": {
            "labels": session_labels,
            "values": session_values,
        },
        "trend": {
            "dates": trend_dates,
            "wasted_meals": trend_wastes,
        },
    })


@api_bp.route("/predict", methods=["POST"])
def api_predict():
    """JSON API endpoint for programmatic prediction."""
    data = request.get_json(silent=True) or request.form
    date_str = data.get("date")
    meal_type = data.get("meal_type")
    menu_name = data.get("menu_name")
    attendance = data.get("attendance")

    if not all([date_str, meal_type, menu_name, attendance]):
        return jsonify({"error": "Missing required fields: date, meal_type, menu_name, attendance"}), 400

    try:
        predictor = get_predictor()
        res = predictor.predict(
            date_str=date_str,
            meal_type=meal_type,
            menu_name=menu_name,
            attendance=int(attendance),
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/export-csv")
def export_csv():
    """Exports all mess records as a downloadable CSV report including workflow metrics."""
    records = MessRecord.query.order_by(MessRecord.record_date.asc(), MessRecord.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header Row
    writer.writerow([
        "Record ID",
        "Date",
        "Day of Week",
        "Meal Session",
        "Menu Name",
        "Hostel Attendance",
        "Prepared Meals",
        "Consumed Meals",
        "Actual Wasted Meals",
        "Waste Percentage (%)",
        "AI Predicted Demand",
        "Estimated Surplus Before Prep",
        "Prediction Error",
        "Notes",
    ])

    for r in records:
        writer.writerow([
            r.id,
            r.record_date.strftime("%Y-%m-%d"),
            r.day_of_week,
            r.meal_type,
            r.menu_name,
            r.attendance,
            r.prepared_meals,
            r.consumed_meals if r.consumed_meals is not None else "Pending",
            r.wasted_meals if r.wasted_meals is not None else "Pending",
            f"{r.waste_percentage}%" if r.waste_percentage is not None else "Pending",
            r.predicted_meals if r.predicted_meals is not None else "N/A",
            f"{r.estimated_surplus:+d}" if r.estimated_surplus is not None else "N/A",
            f"{r.prediction_error:+d}" if r.prediction_error is not None else "N/A",
            r.notes or "",
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=mess_food_waste_report.csv"},
    )
