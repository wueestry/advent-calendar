from __future__ import annotations

from flask.testing import FlaskClient

from advent_calendar.doors import get_door_by_day


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
    response = client.post(
        "/login",
        data={"username": "santa", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert b"Invalid username or password." in response.data


def test_login_with_valid_credentials_and_logout(client: FlaskClient) -> None:
    login_resp = client.post(
        "/login",
        data={"username": "santa", "password": "secret-password"},
        follow_redirects=True,
    )
    assert login_resp.status_code == 200
    assert b"Advent Calendar 2026" in login_resp.data

    logout_resp = client.post("/logout", follow_redirects=True)
    assert logout_resp.status_code == 200
    assert b"You have been logged out." in logout_resp.data

    after_logout = client.get("/")
    assert after_logout.status_code == 302
