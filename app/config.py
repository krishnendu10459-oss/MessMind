"""
=============================================================================
AI-POWERED FOOD WASTE PREDICTION SYSTEM
Module: app/config.py
Description: Dynamic Dual-Database Configuration (MySQL Primary + SQLite Fallback).
Supports URL-encoded credentials (urllib.parse.quote_plus), DATABASE_URL overrides,
controlled fallback flags (ALLOW_SQLITE_FALLBACK), and deterministic startup resolution.
=============================================================================
"""

import os
import re
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


def mask_connection_uri(uri: str) -> str:
    """Masks database credentials and local filesystem paths in a connection URI for safe reporting."""
    if not uri:
        return ""
    # Mask password if standard user:pass@host pattern is present
    masked = re.sub(r":([^/@:]+)@", r":****@", uri)
    # Sanitize SQLite absolute file paths to project-relative paths to prevent host filesystem path disclosure
    if masked.startswith("sqlite:///") and ":memory:" not in masked:
        base_posix = BASE_DIR.as_posix()
        normalized = masked.replace("\\", "/")
        if base_posix in normalized:
            masked = normalized.replace(f"sqlite:///{base_posix}/", "sqlite:///")
        else:
            match = re.search(r"sqlite:///.*/(database/.*\.db)", normalized)
            if match:
                masked = f"sqlite:///{match.group(1)}"
    return masked


class Config:
    """Base application configuration with deterministic database configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-college-2026")
    FLASK_ENV = os.getenv("FLASK_ENV", "development").lower()
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    IS_PRODUCTION = (FLASK_ENV == "production") or (os.getenv("ENV", "").lower() == "production")

    # Controlled Failover Governance:
    # Default is FALSE to prevent silent fallback and data divergence
    ALLOW_SQLITE_FALLBACK = os.getenv("ALLOW_SQLITE_FALLBACK", "false").lower() in ("true", "1", "t", "yes")

    # Database Selection
    # DB_TYPE: 'mysql' (Primary College Submission) or 'sqlite' (Zero-config Local Dev)
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
    env_db_url = os.getenv("DATABASE_URL", "").strip()

    if env_db_url:
        # 1. DATABASE_URL priority override
        if env_db_url.startswith("sqlite:///") and ":memory:" not in env_db_url:
            rel_part = env_db_url[len("sqlite:///"):]
            if not (len(rel_part) > 1 and rel_part[1] == ":") and not rel_part.startswith("/"):
                resolved_file = (BASE_DIR / rel_part).resolve()
                resolved_file.parent.mkdir(parents=True, exist_ok=True)
                SQLALCHEMY_DATABASE_URI = f"sqlite:///{resolved_file.as_posix()}"
            else:
                SQLALCHEMY_DATABASE_URI = env_db_url
        else:
            SQLALCHEMY_DATABASE_URI = env_db_url
        ACTIVE_DB_TYPE = "mysql" if "mysql" in env_db_url.lower() else "sqlite"

    elif DB_TYPE == "mysql":
        # 2. Structured MySQL Configuration with URL-encoded credentials
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "food_waste_db")

        quoted_user = quote_plus(DB_USER)
        quoted_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
        auth = f"{quoted_user}:{quoted_password}" if quoted_password != "" else quoted_user

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
        ACTIVE_DB_TYPE = "mysql"

    else:
        # 3. SQLite Configuration (Standard Local Dev)
        SQLITE_PATH = os.getenv("SQLITE_PATH", "database/food_waste.db")
        db_file = BASE_DIR / SQLITE_PATH if not Path(SQLITE_PATH).is_absolute() else Path(SQLITE_PATH)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file.as_posix()}"
        ACTIVE_DB_TYPE = "sqlite"

    # Connection pooling and resilience options
    if ACTIVE_DB_TYPE == "mysql":
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": 280,
            "pool_pre_ping": True,  # Tests connection before using it
            "pool_size": 10,
            "max_overflow": 20,
            "connect_args": {"connect_timeout": 5},  # Fast failure for unreachable servers
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
        }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Machine learning model paths
    ML_MODEL_PATH = BASE_DIR / "ml_engine" / "saved_models" / "random_forest_model.joblib"
    PREPROCESSOR_PATH = BASE_DIR / "ml_engine" / "saved_models" / "preprocessor.joblib"
    METRICS_PATH = BASE_DIR / "ml_engine" / "saved_models" / "model_metrics.json"

    @classmethod
    def get_masked_uri(cls, uri: str = None) -> str:
        """Returns masked URI with password hidden."""
        target = uri if uri is not None else cls.SQLALCHEMY_DATABASE_URI
        return mask_connection_uri(target)

    @classmethod
    def get_db_info(cls):
        """Returns diagnostic info about active database configuration."""
        return {
            "active_type": cls.ACTIVE_DB_TYPE,
            "configured_type": cls.DB_TYPE,
            "uri_masked": cls.get_masked_uri(),
            "allow_fallback": cls.ALLOW_SQLITE_FALLBACK,
            "is_production": cls.IS_PRODUCTION,
        }
