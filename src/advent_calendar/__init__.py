from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from flask import Flask

from advent_calendar.auth import auth_bp
from advent_calendar.calendar import calendar_bp
from advent_calendar.config import load_config, parse_bool


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(load_config())

    if test_config is not None:
        app.config.from_mapping(test_config)
        if "ENABLE_DEBUG" in test_config:
            app.config["ENABLE_DEBUG"] = parse_bool(test_config["ENABLE_DEBUG"])

    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)

    return app
