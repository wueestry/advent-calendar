from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any


DEFAULT_MEDIA_DIR = Path(__file__).resolve().parent / "media"
DEFAULT_SECRET_KEY = "dev-advent-calendar-secret-key"
DEFAULT_PASSWORD = "advent2026"


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config() -> dict[str, Any]:
    default_year = int(os.environ.get("CALENDAR_YEAR", date.today().year))
    trusted_hosts = _split_csv(os.environ.get("TRUSTED_HOSTS"))
    return {
        # Application

        "APP_ENV": os.environ.get("APP_ENV", "development").strip().lower(),
        "SECRET_KEY": os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY),
        "APP_USERNAME": os.environ.get("APP_USERNAME", "admin"),
        "APP_PASSWORD": os.environ.get("APP_PASSWORD", DEFAULT_PASSWORD),
        "APP_PASSWORD_HASH": os.environ.get("APP_PASSWORD_HASH", ""),
        "ENABLE_DEBUG": parse_bool(os.environ.get("ENABLE_DEBUG", "False")),
        "CALENDAR_YEAR": default_year,
        "TIMEZONE": os.environ.get("TIMEZONE", "Europe/Zurich"),
        "MEDIA_DIR": Path(os.environ.get("MEDIA_DIR", str(DEFAULT_MEDIA_DIR))),
        "CURRENT_DATE": None,

        # Session / authentication hardening. Flask turns these into cookie flags.
        "SESSION_COOKIE_NAME": "advent_calendar_session",
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": parse_bool(os.environ.get("COOKIE_SECURE", "False")),
        "PERMANENT_SESSION_LIFETIME": timedelta(
            hours=int(os.environ.get("SESSION_LIFETIME_HOURS", "12"))
        ),
        "SESSION_IDLE_TIMEOUT": int(
            os.environ.get("SESSION_IDLE_TIMEOUT_MINUTES", "30")
        )
        * 60,
        "SESSION_WARNING_SECONDS": 120,

        # Login throttling (in-memory, per application process).
        "LOGIN_MAX_ATTEMPTS": int(os.environ.get("LOGIN_MAX_ATTEMPTS", "5")),
        "LOGIN_LOCKOUT_SECONDS": int(os.environ.get("LOGIN_LOCKOUT_SECONDS", "900")),

        # CORS is denied by default. Set a comma-separated allowlist to enable it.
        "ALLOWED_ORIGINS": _split_csv(os.environ.get("ALLOWED_ORIGINS")),

        # Transport / header hardening.
        "CSP_REPORT_ONLY": parse_bool(os.environ.get("CSP_REPORT_ONLY", "False")),
        "TRUST_PROXY_HEADERS": parse_bool(
            os.environ.get("TRUST_PROXY_HEADERS", "False")
        ),
        "TRUSTED_HOSTS": trusted_hosts or None,
        "MAX_CONTENT_LENGTH": 1024 * 1024,
        "SEND_FILE_MAX_AGE_DEFAULT": 31536000,
    }
