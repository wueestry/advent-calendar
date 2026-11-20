from __future__ import annotations

import functools
import hmac
from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

auth_bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str | None) -> bool:
    if not target:
        return False
    parts = urlsplit(target)
    return not parts.scheme and not parts.netloc and target.startswith("/")


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(view)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if not session.get("authenticated"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Any:
    if session.get("authenticated"):
        return redirect(url_for("calendar.index"))

    next_url = request.args.get("next") or request.form.get("next") or ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        expected_user = str(current_app.config.get("APP_USERNAME", ""))
        expected_pass = str(current_app.config.get("APP_PASSWORD", ""))

        user_ok = hmac.compare_digest(username, expected_user)
        pass_ok = hmac.compare_digest(password, expected_pass)

        if user_ok and pass_ok:
            session.clear()
            session["authenticated"] = True
            session["username"] = username
            if _is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("calendar.index"))

        flash("Invalid username or password.", "error")
        return render_template("login.html", next_url=next_url), 401

    return render_template("login.html", next_url=next_url)


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout() -> Any:
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
