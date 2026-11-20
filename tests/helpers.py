from __future__ import annotations

import re

from flask.testing import FlaskClient

_CSRF_INPUT = re.compile(rb'name="csrf_token" value="([^"]+)"')


def extract_csrf(response) -> str:
    match = _CSRF_INPUT.search(response.data)
    assert match is not None, "CSRF token not found in response"
    return match.group(1).decode()


def login(
    client: FlaskClient,
    username: str = "santa",
    password: str = "secret-password",
    *,
    follow_redirects: bool = True,
):
    page = client.get("/login")
    token = extract_csrf(page)
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "csrf_token": token,
        },
        follow_redirects=follow_redirects,
    )
