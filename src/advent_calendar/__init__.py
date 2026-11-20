from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from advent_calendar.auth import auth_bp
from advent_calendar.calendar import calendar_bp
from advent_calendar.config import load_config, parse_bool
from advent_calendar.i18n import format_date_de, format_day_month_de
from advent_calendar.security import init_security, validate_config

_BOOL_KEYS = {
    "ENABLE_DEBUG",
    "SESSION_COOKIE_SECURE",
    "CSP_REPORT_ONLY",
    "TRUST_PROXY_HEADERS",
}


def _asset_version(app: Flask) -> str:
    static_dir = Path(app.static_folder or "")
    try:
        latest = max(
            (path.stat().st_mtime_ns for path in static_dir.rglob("*") if path.is_file()),
            default=0,
        )
    except OSError:
        latest = 0
    return str(latest)


def _register_error_handlers(app: Flask) -> None:
    messages = {
        400: (
            "Ungültige Anfrage oder abgelaufenes Sicherheitstoken. "
            "Bitte laden Sie die Seite neu."
        ),
        403: "Zugriff verweigert.",
        404: "Diese Seite wurde nicht gefunden.",
        405: "Diese Aktion ist nicht erlaubt.",
        413: "Die Anfrage ist zu gross.",
        429: "Zu viele Anfragen. Bitte versuchen Sie es später erneut.",
        500: "Ein unerwarteter Fehler ist aufgetreten.",
    }

    def error_page(error: Any) -> Any:
        code = int(getattr(error, "code", 500) or 500)
        message = messages.get(code, messages[500])
        return (
            render_template("error.html", error_code=code, error_message=message),
            code,
        )

    for code in (400, 403, 404, 405, 413, 429, 500):
        app.register_error_handler(code, error_page)


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(load_config())

    if test_config is not None:
        app.config.from_mapping(test_config)
        for key in _BOOL_KEYS:
            if key in test_config:
                app.config[key] = parse_bool(test_config[key])

    validate_config(app)

    if app.config.get("TRUST_PROXY_HEADERS"):
        app.wsgi_app = ProxyFix(  # type: ignore[method-assign]
            app.wsgi_app, x_for=1, x_proto=1, x_host=1
        )

    init_security(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)

    app.jinja_env.filters["date_de"] = format_date_de
    app.jinja_env.filters["day_month_de"] = format_day_month_de
    app.jinja_env.globals["asset_version"] = _asset_version(app)

    _register_error_handlers(app)

    return app
