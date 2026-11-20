from __future__ import annotations

from datetime import date
from pathlib import Path
import pytest

from advent_calendar import create_app
import advent_calendar.doors as doors_module
from advent_calendar.doors import DOORS, Door, get_door_by_day
from advent_calendar.i18n import format_date_de, format_day_month_de
from tests.helpers import login


def test_all_24_doors_have_unique_suids() -> None:
    assert len(DOORS) == 24
    suids = {d.suid for d in DOORS}
    days = [d.day for d in DOORS]
    assert len(suids) == 24
    assert days == list(range(1, 25))


def test_locked_door_redirects_home_with_flash_before_december(auth_client) -> None:
    door1 = get_door_by_day(1)
    assert door1 is not None

    response = auth_client.get(f"/door/{door1.suid}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    followed = auth_client.get(f"/door/{door1.suid}", follow_redirects=True)
    assert followed.status_code == 200
    assert "Tür Nr. 1 ist noch verschlossen!" in followed.get_data(as_text=True)


def test_doors_unlock_on_their_date_and_stay_unlocked_afterwards() -> None:
    # On Dec 10, 2026: doors 1..10 are open, doors 11..24 are locked
    app = create_app(
        {
            "TESTING": True,
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 12, 10),
            "ENABLE_DEBUG": False,
        }
    )
    client = app.test_client()
    login(client)

    door1 = get_door_by_day(1)
    door10 = get_door_by_day(10)
    door11 = get_door_by_day(11)
    assert door1 and door10 and door11

    resp1 = client.get(f"/door/{door1.suid}")
    assert resp1.status_code == 200
    assert door1.title.encode() in resp1.data

    resp10 = client.get(f"/door/{door10.suid}")
    assert resp10.status_code == 200
    assert door10.title.encode() in resp10.data

    resp11 = client.get(f"/door/{door11.suid}", follow_redirects=False)
    assert resp11.status_code == 302
    assert resp11.headers["Location"].endswith("/")


def test_doors_remain_unlocked_after_december_ends() -> None:
    # In January 2027 (after Dec 2026), all 24 doors remain unlocked
    app = create_app(
        {
            "TESTING": True,
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2027, 1, 15),
            "ENABLE_DEBUG": False,
        }
    )
    client = app.test_client()
    login(client)

    door24 = get_door_by_day(24)
    assert door24 is not None
    resp24 = client.get(f"/door/{door24.suid}")
    assert resp24.status_code == 200
    assert door24.title.encode() in resp24.data


def test_enable_debug_env_unlocks_all_doors_regardless_of_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEBUG", "True")
    app = create_app(
        {
            "TESTING": True,
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 7, 1),
        }
    )
    client = app.test_client()
    login(client)

    for door in DOORS:
        resp = client.get(f"/door/{door.suid}")
        assert resp.status_code == 200
        assert f"Tür Nr. {door.day}" in resp.get_data(as_text=True)


def test_unknown_suid_returns_404(auth_client) -> None:
    resp = auth_client.get("/door/nonexistent-suid")
    assert resp.status_code == 404


def test_locked_door_media_redirects_home_with_flash(auth_client) -> None:
    door1 = get_door_by_day(1)
    assert door1 is not None and door1.image is not None

    resp = auth_client.get(f"/door/{door1.suid}/media/{door1.image}", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_unlocked_door_renders_and_serves_picture_and_video(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "festive.svg").write_text("<svg>festive</svg>", encoding="utf-8")
    (tmp_path / "clip.mp4").write_bytes(b"fake-mp4-bytes")

    custom_door = Door(
        day=2,
        suid="d4e8b2109c7a",
        title="Media Door",
        subtitle="December 2",
        content="Door with picture, local video, and embed.",
        image="festive.svg",
        image_alt="Festive vector",
        video="clip.mp4",
        youtube_embed="https://www.youtube.com/embed/dQw4w9WgXcQ",
    )
    monkeypatch.setitem(doors_module.DOORS_BY_SUID, custom_door.suid, custom_door)

    app = create_app(
        {
            "TESTING": True,
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 12, 2),
            "ENABLE_DEBUG": False,
            "MEDIA_DIR": tmp_path,
        }
    )
    client = app.test_client()
    login(client)

    page = client.get(f"/door/{custom_door.suid}")
    assert page.status_code == 200
    assert f'/door/{custom_door.suid}/media/festive.svg'.encode() in page.data
    assert f'/door/{custom_door.suid}/media/clip.mp4'.encode() in page.data
    assert b"https://www.youtube.com/embed/dQw4w9WgXcQ" in page.data

    img_resp = client.get(f"/door/{custom_door.suid}/media/festive.svg")
    assert img_resp.status_code == 200
    assert b"<svg>festive</svg>" in img_resp.data

    vid_resp = client.get(f"/door/{custom_door.suid}/media/clip.mp4")
    assert vid_resp.status_code == 200
    assert vid_resp.data == b"fake-mp4-bytes"

    # Requesting a file not attached to this door returns 404
    other_resp = client.get(f"/door/{custom_door.suid}/media/day1-candle.svg")
    assert other_resp.status_code == 404


def test_german_date_formatting() -> None:
    assert format_date_de(date(2026, 12, 4)) == "4. Dezember 2026"
    assert format_day_month_de(date(2026, 12, 4)) == "4. Dezember"


def test_index_is_localized_in_swiss_german() -> None:
    app = create_app(
        {
            "TESTING": True,
            "APP_USERNAME": "santa",
            "APP_PASSWORD": "secret-password",
            "CALENDAR_YEAR": 2026,
            "CURRENT_DATE": date(2026, 12, 4),
            "ENABLE_DEBUG": False,
        }
    )
    client = app.test_client()
    login(client)

    page = client.get("/").get_data(as_text=True)
    assert 'lang="de-CH"' in page
    assert "Heute ist" in page
    assert "4. Dezember 2026" in page
    assert "Öffnet am 24. Dezember" in page
    assert "Verschlossen" in page
