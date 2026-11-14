from __future__ import annotations

from datetime import date
import pytest

from advent_calendar import create_app
from advent_calendar.doors import DOORS, get_door_by_day


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
    assert b"Door #1 is still locked!" in followed.data


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
    client.post("/login", data={"username": "santa", "password": "secret-password"})

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
    client.post("/login", data={"username": "santa", "password": "secret-password"})

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
    client.post("/login", data={"username": "santa", "password": "secret-password"})

    for door in DOORS:
        resp = client.get(f"/door/{door.suid}")
        assert resp.status_code == 200
        assert f"Door #{door.day}".encode() in resp.data


def test_unknown_suid_returns_404(auth_client) -> None:
    resp = auth_client.get("/door/nonexistent-suid")
    assert resp.status_code == 404
