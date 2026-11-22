from __future__ import annotations

import functools
import hmac
import secrets
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import unquote, urlsplit

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
from werkzeug.security import check_password_hash

from advent_calendar.security import (
    get_login_limiter,
    register_session,
    revoke_session,
)

auth_bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str | None) -> bool:
    if not target:
        return False
    decoded = unquote(target)
    parts = urlsplit(decoded)
    return (
        not parts.scheme
        and not parts.netloc
        and decoded.startswith("/")
        and not decoded.startswith("//")
        and "\\" not in decoded
        and all(ord(char) >= 32 for char in decoded)
    )


def _secure_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def _verify_credentials(username: str, password: str) -> bool:
    expected_user = str(current_app.config.get("APP_USERNAME", ""))
    password_hash = str(current_app.config.get("APP_PASSWORD_HASH", "") or "")

    user_ok = _secure_compare(username, expected_user)
    if password_hash:
        pass_ok = check_password_hash(password_hash, password)
    else:
        expected_pass = str(current_app.config.get("APP_PASSWORD", ""))
        pass_ok = _secure_compare(password, expected_pass)
    return user_ok and pass_ok


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
        limiter = get_login_limiter()
        client_key = request.remote_addr or "unknown"
        retry_after = limiter.retry_after(client_key)
        if retry_after:
            flash(
                "Zu viele fehlgeschlagene Anmeldeversuche. "
                "Bitte versuchen Sie es in einigen Minuten erneut.",
                "error",
            )
            response = current_app.make_response(
                render_template("login.html", next_url=next_url)
            )
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            return response

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if _verify_credentials(username, password):
            limiter.reset(client_key)
            revoke_session()
            session.clear()
            session.permanent = True
            session["authenticated"] = True
            session["username"] = username
            session["created_at"] = time.time()
            session["last_seen"] = time.time()
            session["_csrf_token"] = secrets.token_urlsafe(32)
            register_session()
            if _is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("calendar.index"))

        limiter.register_failure(client_key)
        flash("Benutzername oder Passwort ist ungültig.", "error")
        return render_template("login.html", next_url=next_url), 401

    return render_template("login.html", next_url=next_url)


@auth_bp.route("/logout", methods=["POST"])
def logout() -> Any:
    revoke_session()
    session.clear()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))
