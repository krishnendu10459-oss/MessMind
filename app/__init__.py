"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: app/__init__.py
Description: Flask Application Factory with Strict Dual-Database Governance,
Production Fail-Fast Enforcement, Controlled Development Fallback,
SQLite foreign key pragma listener, CSRF Protection, and Safe Error Handlers.
=============================================================================
"""

import logging
import secrets
from flask import Flask, session, request, abort, render_template
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.config import Config, BASE_DIR
from app.extensions import db, migrate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FoodWasteAI")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforces SQLite foreign key integrity constraints automatically."""
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def generate_csrf_token():
    """Generates and persists a cryptographically secure CSRF token in session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def create_app(config_class=Config):
    """Application factory for the AI Food Waste Prediction System."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Propagate explicit DB settings to app config
    target_uri = flask_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    target_type = getattr(config_class, "ACTIVE_DB_TYPE", "mysql" if "mysql" in target_uri else "sqlite")
    flask_app.config["ACTIVE_DB_TYPE"] = target_type
    flask_app.config["DB_FALLBACK_ACTIVE"] = False
    flask_app.config["DB_STATUS"] = "initializing"
    flask_app.config["ALLOW_SQLITE_FALLBACK"] = getattr(config_class, "ALLOW_SQLITE_FALLBACK", False)
    flask_app.config["IS_PRODUCTION"] = getattr(config_class, "IS_PRODUCTION", False)

    # Register CSRF generator in Jinja environment
    flask_app.jinja_env.globals["csrf_token"] = generate_csrf_token

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Strict Startup Verification
    with flask_app.app_context():
        from app.models.mess_record import MessRecord, PredictionLog, SurplusAdvisory

        is_mysql = ("mysql" in target_uri.lower()) or (target_type == "mysql")
        is_production = flask_app.config.get("IS_PRODUCTION", False)
        allow_fallback = flask_app.config.get("ALLOW_SQLITE_FALLBACK", False)
        masked_target = Config.get_masked_uri(target_uri)

        try:
            # Test live connection
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database connected successfully: {masked_target} [{target_type.upper()}]")
            db.create_all()
            flask_app.config["DB_STATUS"] = "connected"
            flask_app.config["DB_FALLBACK_ACTIVE"] = False

        except (OperationalError, SQLAlchemyError, Exception) as e:
            if is_mysql:
                if is_production:
                    # In production: Fail hard. NEVER fall back to SQLite to prevent data inconsistency.
                    error_msg = (
                        f"🛑 FATAL [PRODUCTION]: Cannot connect to primary MySQL database at {masked_target}. "
                        f"Root cause: {e}. "
                        "Automatic SQLite fallback is strictly prohibited in production to prevent data divergence. "
                        "Startup aborted."
                    )
                    logger.critical(error_msg)
                    flask_app.config["DB_STATUS"] = "failed"
                    raise RuntimeError(error_msg) from e

                # In development mode:
                if allow_fallback:
                    logger.warning(
                        f"⚠️ [DEVELOPMENT WARNING]: Could not connect to MySQL ({e}). "
                        "Controlled fallback ACTIVATED: Switching to SQLite local database at database/food_waste.db "
                        "because ALLOW_SQLITE_FALLBACK=true."
                    )
                    # Reconfigure to local SQLite and reset MySQL-specific engine options
                    sqlite_file = BASE_DIR / "database" / "food_waste.db"
                    sqlite_file.parent.mkdir(parents=True, exist_ok=True)
                    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_file.as_posix()}"
                    flask_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
                    flask_app.config["ACTIVE_DB_TYPE"] = "sqlite"
                    flask_app.config["DB_FALLBACK_ACTIVE"] = True
                    flask_app.config["DB_STATUS"] = "degraded"

                    # Re-initialize engine cleanly with SQLite
                    if "sqlalchemy" in flask_app.extensions:
                        del flask_app.extensions["sqlalchemy"]
                    db.init_app(flask_app)
                    db.create_all()
                    logger.info("✅ Controlled SQLite local fallback initialized successfully.")

                else:
                    # Fallback is NOT allowed (default): Fail fast with clear diagnostic instructions
                    error_msg = (
                        f"❌ [STARTUP ERROR]: Failed to connect to MySQL database at {masked_target}. "
                        f"Error: {e}. "
                        "Silent database switching is disabled (ALLOW_SQLITE_FALLBACK=false). "
                        "To prevent accidental data divergence, startup has been stopped. "
                        "To resolve:\n"
                        "  1. Start your local MySQL service (e.g. XAMPP / MySQL Workbench / Docker), OR\n"
                        "  2. In .env set DB_TYPE=sqlite for standard local development, OR\n"
                        "  3. In .env set ALLOW_SQLITE_FALLBACK=true to explicitly allow development fallback."
                    )
                    logger.error(error_msg)
                    flask_app.config["DB_STATUS"] = "failed"
                    raise RuntimeError(error_msg) from e
            else:
                # Target was SQLite and failed
                logger.error(f"❌ SQLite database initialization error: {e}")
                flask_app.config["DB_STATUS"] = "failed"
                raise

    # Context processor to inject database status into all templates
    @flask_app.context_processor
    def inject_db_status():
        return {
            "db_info": {
                "type": flask_app.config.get("ACTIVE_DB_TYPE", "sqlite"),
                "is_fallback": flask_app.config.get("DB_FALLBACK_ACTIVE", False),
                "status": flask_app.config.get("DB_STATUS", "unknown"),
            }
        }

    # CSRF Protection Middleware for all state-modifying requests
    @flask_app.before_request
    def validate_csrf():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Programmatic API endpoints under /api/* use token/auth or JSON payloads
            if request.path.startswith("/api/"):
                return
            # Allow tests to disable CSRF check via configuration
            if flask_app.config.get("TESTING") and not flask_app.config.get("WTF_CSRF_ENABLED", True):
                return

            expected_token = session.get("_csrf_token")
            received_token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")

            if not expected_token or not received_token or not secrets.compare_digest(expected_token, received_token):
                logger.warning(f"🛡️ CSRF block triggered on {request.path} from IP {request.remote_addr}")
                abort(403, description="Security check failed: CSRF token missing or invalid. Please refresh the page and try again.")

    # Database session cleanup
    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Production-safe custom error handlers (no internal paths or stack traces leaked)
    @flask_app.errorhandler(400)
    def bad_request_error(e):
        desc = getattr(e, "description", "The browser sent a request that this server could not understand.")
        return render_template("error.html", error_code=400, title="Bad Request", message=desc), 400

    @flask_app.errorhandler(403)
    def forbidden_error(e):
        desc = getattr(e, "description", "You do not have permission to access the requested resource.")
        return render_template("error.html", error_code=403, title="Forbidden", message=desc), 403

    @flask_app.errorhandler(404)
    def not_found_error(e):
        return render_template("error.html", error_code=404, title="Page Not Found", message="The requested URL was not found on this server. Check the address or return to the dashboard."), 404

    @flask_app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        msg = "An internal server error occurred. Our administration log has been updated." if flask_app.config.get("IS_PRODUCTION") else f"Internal Server Error: {str(e)}"
        return render_template("error.html", error_code=500, title="Server Error", message=msg), 500

    # Register Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(api_bp)

    return flask_app
