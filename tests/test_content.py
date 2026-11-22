from __future__ import annotations

from datetime import date

from flask import Flask
import pytest

from advent_calendar import create_app
import advent_calendar.doors as doors_module
from advent_calendar.doors import Door
from advent_calendar.formatting import format_content
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
            "CURRENT_DATE": date(2026, 12, 3),
            "ENABLE_DEBUG": False,
        }
    )


def test_format_content_turns_newlines_into_line_breaks() -> None:
    rendered = str(format_content("Erste Zeile\nZweite Zeile\nDritte Zeile"))

    assert rendered == "Erste Zeile<br>\nZweite Zeile<br>\nDritte Zeile"


def test_format_content_normalizes_windows_and_old_mac_newlines() -> None:
    assert str(format_content("Eins\r\nZwei\rDrei")) == "Eins<br>\nZwei<br>\nDrei"


def test_format_content_escapes_html() -> None:
    rendered = str(format_content('<script>alert("x")</script>\n<b>bold</b>'))

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&lt;b&gt;bold&lt;/b&gt;" in rendered


def test_door_content_renders_line_breaks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    custom_door = Door(
        day=3,
        suid="linebreak-door",
        title="Zeilenumbruch",
        subtitle="Test",
        content="Erste Zeile\nZweite Zeile",
    )
    monkeypatch.setitem(doors_module.DOORS_BY_SUID, custom_door.suid, custom_door)

    app = _create_app()
    client = app.test_client()
    login(client)

    page = client.get(f"/door/{custom_door.suid}").get_data(as_text=True)

    assert "Erste Zeile<br>" in page
    assert "Zweite Zeile" in page
