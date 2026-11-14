from __future__ import annotations

from datetime import date
import pytest
from flask import Flask
from flask.testing import FlaskClient

from advent_calendar import create_app


@pytest.fixture
def app() -> Flask:
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 11, 14),
            "ENABLE_DEBUG": False,
        }
    )


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def auth_client(client: FlaskClient) -> FlaskClient:
    client.post(
        "/login",
        data={"username": "santa", "password": "secret-password"},
        follow_redirects=True,
    )
    return client
