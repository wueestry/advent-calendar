from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any


DEFAULT_MEDIA_DIR = Path(__file__).resolve().parent / "media"


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def load_config() -> dict[str, Any]:
    default_year = int(os.environ.get("CALENDAR_YEAR", date.today().year))
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-advent-calendar-secret-key"),
        "APP_USERNAME": os.environ.get("APP_USERNAME", "admin"),
        "APP_PASSWORD": os.environ.get("APP_PASSWORD", "advent2026"),
        "ENABLE_DEBUG": parse_bool(os.environ.get("ENABLE_DEBUG", "False")),
        "CALENDAR_YEAR": default_year,
        "TIMEZONE": os.environ.get("TIMEZONE", "UTC"),
        "MEDIA_DIR": Path(os.environ.get("MEDIA_DIR", str(DEFAULT_MEDIA_DIR))),
        "CURRENT_DATE": None,
    }
