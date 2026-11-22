from __future__ import annotations

from datetime import date

from flask import Flask
from flask.testing import FlaskClient

from advent_calendar import create_app
import advent_calendar.security as security


def test_login_lockout_expires(monkeypatch) -> None:
    class FakeTime:
        value = 1000.0

        @classmethod
        def time(cls) -> float:
            return cls.value

    monkeypatch.setattr(security, "time", FakeTime)
    limiter = security.LoginRateLimiter(max_attempts=2, lockout_seconds=60)

    limiter.register_failure("client")
    limiter.register_failure("client")
    assert limiter.retry_after("client") == 60

    FakeTime.value += 61
    assert limiter.retry_after("client") == 0


def _create_app(**overrides) -> Flask:
    config = {
        "TESTING": True,
        "APP_ENV": "testing",
        "SECRET_KEY": "test-secret",
        "APP_USERNAME": "santa",
        "APP_PASSWORD": "secret-password",
        "CALENDAR_YEAR": 2026,
        "CURRENT_DATE": date(2026, 12, 4),
        "ENABLE_DEBUG": False,
    }
    config.update(overrides)
    return create_app(config)


def test_security_headers_are_present(client: FlaskClient) -> None:
    response = client.get("/login")
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_hsts_header_is_present_on_http_responses(client: FlaskClient) -> None:
    response = client.get("/login")
    assert response.headers["Strict-Transport-Security"] == (
        "max-age=63072000; includeSubDomains"
    )


def test_html_responses_are_not_cached(client: FlaskClient) -> None:
    response = client.get("/login")
    assert response.headers["Cache-Control"] == "no-store, max-age=0"
    assert response.headers["Pragma"] == "no-cache"


def test_static_assets_are_cached_immutably(client: FlaskClient) -> None:
    response = client.get("/static/style.css")
    cache_control = response.headers["Cache-Control"]
    assert "public" in cache_control
    assert "immutable" in cache_control
    assert "max-age=31536000" in cache_control


def test_cors_is_denied_by_default(client: FlaskClient) -> None:
    get_response = client.get(
        "/login", headers={"Origin": "https://evil.example"}
    )
    assert "Access-Control-Allow-Origin" not in get_response.headers

    preflight = client.open(
        "/login",
        method="OPTIONS",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code == 403


def test_cors_allows_configured_origins() -> None:
    app = _create_app(ALLOWED_ORIGINS=["https://example.com"])
    client = app.test_client()

    response = client.get("/login", headers={"Origin": "https://example.com"})
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"

    preflight = client.open(
        "/login",
        method="OPTIONS",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert preflight.status_code == 204
    assert preflight.headers["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
    assert "X-CSRF-Token" in preflight.headers["Access-Control-Allow-Headers"]


def test_unknown_route_renders_german_error_page(auth_client: FlaskClient) -> None:
    response = auth_client.get("/gibt-es-nicht")
    assert response.status_code == 404
    body = response.get_data(as_text=True)
    assert "Diese Seite wurde nicht gefunden." in body
    assert "Zurück zum Adventskalender" in body
