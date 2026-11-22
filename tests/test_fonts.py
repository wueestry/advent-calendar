from __future__ import annotations

from datetime import date

from flask import Flask
from flask.testing import FlaskClient
import pytest

from advent_calendar import create_app
import advent_calendar.doors as doors_module
from advent_calendar.doors import Door
from tests.helpers import login


def _create_app() -> Flask:
    return create_app(
        {
            "TESTING": True,
            "APP_ENV": "testing",
            "SECRET_KEY": "test-secret",
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 12, 4),
            "ENABLE_DEBUG": False,
        }
    )


def test_stylesheet_declares_bundled_nerdfont_fallback(client: FlaskClient) -> None:
    css = client.get("/static/style.css").get_data(as_text=True)

    assert "@font-face" in css
    assert 'font-family: "Nerd Font Symbols";' in css
    assert 'url("fonts/SymbolsNerdFont-Regular.woff2") format("woff2")' in css
    assert "U+E000-F8FF" in css
    assert '"Nerd Font Symbols",' in css


def test_bundled_nerdfont_is_served_and_cached(client: FlaskClient) -> None:
    response = client.get("/static/fonts/SymbolsNerdFont-Regular.woff2")

    assert response.status_code == 200
    assert response.data[:4] == b"wOF2"
    assert "public" in response.headers["Cache-Control"]
    assert "immutable" in response.headers["Cache-Control"]
    assert "max-age=31536000" in response.headers["Cache-Control"]


def test_door_content_preserves_nerdfont_glyphs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    glyph = "\ue0b0"
    custom_door = Door(
        day=4,
        suid="nerdfont-door",
        title="Nerd Font",
        subtitle="Test",
        content=f"Vorher {glyph} Nachher",
    )
    monkeypatch.setitem(doors_module.DOORS_BY_SUID, custom_door.suid, custom_door)

    app = _create_app()
    client = app.test_client()
    login(client)

    page = client.get(f"/door/{custom_door.suid}").get_data(as_text=True)

    assert glyph in page
