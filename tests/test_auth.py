from __future__ import annotations

import time

from flask import Flask
from flask.testing import FlaskClient
import pytest

from advent_calendar import create_app
from advent_calendar.doors import get_door_by_day
from tests.helpers import extract_csrf, login


def test_unauthenticated_home_redirects_to_login(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 302
    assert "/login?next=/" in response.headers["Location"]


def test_unauthenticated_door_redirects_to_login(client: FlaskClient) -> None:
    door1 = get_door_by_day(1)
    assert door1 is not None
    response = client.get(f"/door/{door1.suid}")
    assert response.status_code == 302
    assert f"/login?next=/door/{door1.suid}" in response.headers["Location"]


def test_login_with_invalid_credentials_fails(client: FlaskClient) -> None:
    response = login(client, password="wrong-password", follow_redirects=False)
    assert response.status_code == 401
    assert "Benutzername oder Passwort ist ungültig." in response.get_data(as_text=True)


def test_login_with_valid_credentials_and_logout(client: FlaskClient) -> None:
    login_resp = login(client)
    assert login_resp.status_code == 200
    assert "Adventskalender 2026" in login_resp.get_data(as_text=True)

    token = extract_csrf(login_resp)
    logout_resp = client.post(
        "/logout", data={"csrf_token": token}, follow_redirects=True
    )
    assert logout_resp.status_code == 200
    assert "Sie wurden abgemeldet." in logout_resp.get_data(as_text=True)

    after_logout = client.get("/")
    assert after_logout.status_code == 302


def test_login_requires_csrf_token(client: FlaskClient) -> None:
    response = client.post(
        "/login",
        data={"username": "santa", "password": "secret-password"},
    )
    assert response.status_code == 400
    assert "Sicherheitstoken" in response.get_data(as_text=True)


def test_non_ascii_username_is_rejected_without_server_error(
    client: FlaskClient,
) -> None:
    response = login(client, username="sänta", password="falsch", follow_redirects=False)
    assert response.status_code == 401
    assert "Benutzername oder Passwort ist ungültig." in response.get_data(
        as_text=True
    )


def test_logout_requires_csrf_token(auth_client: FlaskClient) -> None:
    response = auth_client.post("/logout")
    assert response.status_code == 400


def test_login_does_not_redirect_to_external_urls(client: FlaskClient) -> None:
    page = client.get("/login?next=https://evil.example/phish")
    token = extract_csrf(page)
    for target in ("https://evil.example/phish", "//evil.example", "/%5Cevil.example"):
        response = client.post(
            "/login",
            data={
                "username": "santa",
                "password": "secret-password",
                "next": target,
                "csrf_token": token,
            },
        )
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
        # Log out again for the next round.
        with client.session_transaction() as session:
            session.clear()
        page = client.get("/login")
        token = extract_csrf(page)


def test_session_cookie_is_hardened(client: FlaskClient) -> None:
    page = client.get("/login")
    token = extract_csrf(page)
    response = client.post(
        "/login",
        data={
            "username": "santa",
            "password": "secret-password",
            "csrf_token": token,
        },
    )
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie  # COOKIE_SECURE defaults to False for local HTTP


def test_login_attempts_are_rate_limited() -> None:
    app = create_app(
        {
            "TESTING": True,
            "APP_ENV": "testing",
            "SECRET_KEY": "test-secret",
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "LOGIN_MAX_ATTEMPTS": 3,
            "LOGIN_LOCKOUT_SECONDS": 60,
        }
    )
    client = app.test_client()
    page = client.get("/login")
    token = extract_csrf(page)

    data = {
        "username": "santa",
        "password": "wrong-password",
        "csrf_token": token,
    }
    for _ in range(3):
        response = client.post("/login", data=data)
        assert response.status_code == 401

    blocked = client.post("/login", data=data)
    assert blocked.status_code == 429
    assert "Zu viele fehlgeschlagene Anmeldeversuche" in blocked.get_data(
        as_text=True
    )
    assert int(blocked.headers["Retry-After"]) > 0


def test_idle_session_logs_out_automatically(
    app: Flask, auth_client: FlaskClient
) -> None:
    with auth_client.session_transaction() as session:
        session["last_seen"] = time.time() - (
            int(app.config["SESSION_IDLE_TIMEOUT"]) + 60
        )

    response = auth_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    followed = auth_client.get("/", follow_redirects=True)
    assert "automatisch abgemeldet" in followed.get_data(as_text=True)


def test_absolute_session_lifetime_logs_out(
    app: Flask, auth_client: FlaskClient
) -> None:
    with auth_client.session_transaction() as session:
        session["created_at"] = time.time() - (
            app.config["PERMANENT_SESSION_LIFETIME"].total_seconds() + 60
        )

    followed = auth_client.get("/", follow_redirects=True)
    assert "Ihre Sitzung ist abgelaufen" in followed.get_data(as_text=True)


def test_production_rejects_default_secrets() -> None:
    with pytest.raises(RuntimeError, match="Unsafe production configuration"):
        create_app(
            {
                "TESTING": True,
                "APP_ENV": "production",
                "SECRET_KEY": "dev-advent-calendar-secret-key",
                "APP_PASSWORD": "advent2026",
            }
        )


def test_production_rejects_placeholder_secret() -> None:
    with pytest.raises(RuntimeError, match="Unsafe production configuration"):
        create_app(
            {
                "TESTING": True,
                "APP_ENV": "production",
                "SECRET_KEY": "change-me-in-production",
                "APP_PASSWORD": "a-strong-password",
            }
        )


def test_production_rejects_debug_mode() -> None:
    with pytest.raises(RuntimeError, match="ENABLE_DEBUG"):
        create_app(
            {
                "TESTING": True,
                "APP_ENV": "production",
                "SECRET_KEY": "a" * 40,
                "APP_PASSWORD": "a-strong-password",
                "ENABLE_DEBUG": True,
            }
        )
