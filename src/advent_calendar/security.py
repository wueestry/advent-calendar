from __future__ import annotations

import hmac
import math
import secrets
import threading
import time
from datetime import timedelta
from typing import Any

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    redirect,
    request,
    session,
    url_for,
)

from advent_calendar.config import DEFAULT_PASSWORD, DEFAULT_SECRET_KEY, parse_bool

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
SESSION_NONCE_KEY = "session_nonce"
INSECURE_SECRET_KEYS = {
    "",
    DEFAULT_SECRET_KEY,
    "change-me",
    "change-me-in-production",
}

CSP_DEFAULT = (
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "script-src 'self'",
    "style-src 'self'",
    "img-src 'self' data: https:",
    "media-src 'self' https:",
    "font-src 'self'",
    "connect-src 'self'",
    "frame-src https://www.youtube-nocookie.com https://www.youtube.com",
    "manifest-src 'self'",
    "worker-src 'none'",
    "require-trusted-types-for 'script'",
)


class SessionRegistry:
    """Tracks live session nonces so logout can revoke signed cookies.

    Flask sessions are client-side signed cookies. Clearing the cookie does not
    stop a captured copy from being replayed while its signature and timestamps
    are still valid. Registering a random nonce at login and removing it at
    logout gives the server a way to reject such replays. State is process-local,
    matching the app's single-worker deployment.
    """

    def __init__(self, lifetime_seconds: float) -> None:
        self.lifetime_seconds = max(0.0, float(lifetime_seconds))
        self._lock = threading.Lock()
        self._expiries: dict[str, float] = {}

    def register(self, nonce: str, now: float | None = None) -> None:
        current = time.time() if now is None else now
        with self._lock:
            self._purge_expired_locked(current)
            self._expiries[nonce] = (
                current + self.lifetime_seconds if self.lifetime_seconds > 0 else 0.0
            )

    def is_active(self, nonce: str, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        with self._lock:
            expires_at = self._expiries.get(nonce)
            if expires_at is None:
                return False
            if expires_at and expires_at <= current:
                self._expiries.pop(nonce, None)
                return False
            return True

    def revoke(self, nonce: str) -> None:
        with self._lock:
            self._expiries.pop(nonce, None)

    def _purge_expired_locked(self, now: float) -> None:
        for nonce, expires_at in list(self._expiries.items()):
            if expires_at and expires_at <= now:
                self._expiries.pop(nonce, None)


class LoginRateLimiter:
    """Small in-memory throttler for failed login attempts.

    The app is deployed as a single process, so process-local state is enough.
    Behind a multi-worker server each worker keeps its own counter.
    """

    def __init__(self, max_attempts: int, lockout_seconds: int) -> None:
        self.max_attempts = max(1, int(max_attempts))
        self.lockout_seconds = max(1, int(lockout_seconds))
        self._lock = threading.Lock()
        self._attempts: dict[str, tuple[int, float]] = {}

    def retry_after(self, key: str) -> int:
        now = time.time()
        with self._lock:
            failures, locked_until = self._attempts.get(key, (0, 0.0))
            if locked_until > now:
                return max(1, math.ceil(locked_until - now))
            if locked_until:
                self._attempts.pop(key, None)
                return 0
            if failures >= self.max_attempts:
                # Defensive fallback; normally register_failure sets locked_until.
                return self.lockout_seconds
            return 0

    def register_failure(self, key: str) -> None:
        now = time.time()
        with self._lock:
            failures, locked_until = self._attempts.get(key, (0, 0.0))
            if locked_until and locked_until <= now:
                failures = 0
                locked_until = 0.0
            failures += 1
            if failures >= self.max_attempts:
                locked_until = now + self.lockout_seconds
            self._attempts[key] = (failures, locked_until)

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


def validate_config(app: Flask) -> None:
    """Reject unsafe defaults in production and warn about them elsewhere."""
    env = str(app.config.get("APP_ENV", "development")).lower()
    is_production = env in {"production", "prod"}
    secret_key = str(app.config.get("SECRET_KEY", ""))
    password = str(app.config.get("APP_PASSWORD", ""))
    password_hash = str(app.config.get("APP_PASSWORD_HASH", "") or "")
    problems: list[str] = []

    if is_production:
        if secret_key in INSECURE_SECRET_KEYS:
            problems.append(
                "SECRET_KEY must be set to a strong, unique value in production."
            )
        elif len(secret_key) < 32:
            app.logger.warning(
                "SECRET_KEY is shorter than 32 characters; use a longer random value."
            )
        if not password_hash and password in {"", DEFAULT_PASSWORD}:
            problems.append(
                "APP_PASSWORD (or APP_PASSWORD_HASH) must be changed in production."
            )
        if parse_bool(app.config.get("ENABLE_DEBUG")):
            problems.append(
                "ENABLE_DEBUG must be disabled in production; it unlocks all doors."
            )
        if not app.config.get("SESSION_COOKIE_SECURE"):
            app.logger.warning(
                "SESSION_COOKIE_SECURE is disabled. Set COOKIE_SECURE=True when "
                "the app is served over HTTPS."
            )
    else:
        if secret_key in INSECURE_SECRET_KEYS:
            app.logger.warning(
                "Using the development SECRET_KEY. Set a unique SECRET_KEY before "
                "deploying."
            )
        if not password_hash and password in {"", DEFAULT_PASSWORD}:
            app.logger.warning(
                "Using the development APP_PASSWORD. Change it before deploying."
            )

    if problems:
        raise RuntimeError(
            "Unsafe production configuration:\n- " + "\n- ".join(problems)
        )


def get_csrf_token() -> str:
    token = session.get("_csrf_token")
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def get_login_limiter() -> LoginRateLimiter:
    return current_app.extensions["login_rate_limiter"]


def get_session_registry() -> SessionRegistry:
    return current_app.extensions["session_registry"]


def register_session() -> None:
    nonce = secrets.token_urlsafe(32)
    session[SESSION_NONCE_KEY] = nonce
    get_session_registry().register(nonce)


def revoke_session() -> None:
    nonce = session.get(SESSION_NONCE_KEY)
    if isinstance(nonce, str):
        get_session_registry().revoke(nonce)


def _allowed_origins(app: Flask) -> set[str]:
    raw = app.config.get("ALLOWED_ORIGINS", [])
    if isinstance(raw, str):
        items = raw.split(",")
    else:
        items = raw or []
    return {str(origin).strip().rstrip("/") for origin in items if str(origin).strip()}


def _constant_time_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def _csrf_protect() -> Any:
    if request.method in SAFE_METHODS:
        return None
    expected = session.get("_csrf_token")
    supplied = request.form.get("csrf_token") or request.headers.get(
        "X-CSRF-Token", ""
    )
    if (
        not isinstance(expected, str)
        or not supplied
        or not _constant_time_equal(expected, str(supplied))
    ):
        abort(
            400,
            description=(
                "Ungültiges oder fehlendes Sicherheitstoken. "
                "Bitte laden Sie die Seite neu und versuchen Sie es erneut."
            ),
        )
    return None


def _expire_session(message: str) -> Any:
    revoke_session()
    session.clear()
    flash(message, "info")
    if request.endpoint == "auth.login":
        return None
    return redirect(url_for("auth.login"))


def _seconds(value: Any) -> float:
    if isinstance(value, timedelta):
        return value.total_seconds()
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _enforce_session_timeout() -> Any:
    if request.endpoint == "static" or not session.get("authenticated"):
        return None

    nonce = session.get(SESSION_NONCE_KEY)
    if not isinstance(nonce, str) or not get_session_registry().is_active(nonce):
        return _expire_session(
            "Ihre Sitzung ist nicht mehr gültig. Bitte melden Sie sich erneut an."
        )

    now = time.time()

    lifetime = _seconds(current_app.config.get("PERMANENT_SESSION_LIFETIME", 0))
    created_at = session.get("created_at")
    if created_at is None:
        session["created_at"] = now
    elif lifetime > 0:
        try:
            created_value = float(created_at)
        except (TypeError, ValueError):
            created_value = now
        if now - created_value > lifetime:
            return _expire_session(
                "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an."
            )

    timeout = int(current_app.config.get("SESSION_IDLE_TIMEOUT", 0) or 0)
    if timeout <= 0:
        return None

    last_seen = session.get("last_seen")
    if last_seen is not None:
        try:
            last_seen_value = float(last_seen)
        except (TypeError, ValueError):
            last_seen_value = now
        if now - last_seen_value > timeout:
            return _expire_session(
                "Sie wurden aus Sicherheitsgründen automatisch abgemeldet."
            )

    session["last_seen"] = now
    return None


def _cors_preflight() -> Any:
    if request.method != "OPTIONS" or not request.headers.get(
        "Access-Control-Request-Method"
    ):
        return None

    origin = request.headers.get("Origin", "")
    if origin not in current_app.extensions["allowed_origins"]:
        abort(403, description="Diese Herkunft ist für CORS nicht freigegeben.")
    if request.headers.get("Access-Control-Request-Method", "").upper() not in {
        "GET",
        "POST",
        "OPTIONS",
    }:
        abort(403, description="Diese HTTP-Methode ist für CORS nicht freigegeben.")

    response = current_app.response_class(status=204)
    _add_cors_headers(response, origin, preflight=True)
    return response


def _add_cors_headers(response: Any, origin: str, *, preflight: bool = False) -> None:
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.vary.add("Origin")
    if preflight:
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, X-CSRF-Token"
        )
        response.headers["Access-Control-Max-Age"] = "600"


def _security_headers(response: Any) -> Any:
    csp = "; ".join(CSP_DEFAULT)
    policy_header = (
        "Content-Security-Policy-Report-Only"
        if current_app.config.get("CSP_REPORT_ONLY")
        else "Content-Security-Policy"
    )
    response.headers.setdefault(policy_header, csp)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy",
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()",
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
    response.headers.setdefault("X-XSS-Protection", "0")
    response.headers.setdefault("X-Robots-Tag", "noindex, nofollow")

    response.headers.setdefault(
        "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
    )

    origin = request.headers.get("Origin", "")
    if origin and origin in current_app.extensions["allowed_origins"]:
        _add_cors_headers(response, origin)

    if request.endpoint == "static":
        response.cache_control.public = True
        response.cache_control.max_age = int(
            current_app.config.get("SEND_FILE_MAX_AGE_DEFAULT", 31536000)
        )
        response.cache_control.immutable = True
        response.vary.add("Accept-Encoding")
    elif request.endpoint == "calendar.door_media":
        response.cache_control.private = True
        response.cache_control.max_age = 3600
    else:
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"

    return response


def init_security(app: Flask) -> None:
    app.extensions["login_rate_limiter"] = LoginRateLimiter(
        int(app.config.get("LOGIN_MAX_ATTEMPTS", 5)),
        int(app.config.get("LOGIN_LOCKOUT_SECONDS", 900)),
    )
    app.extensions["session_registry"] = SessionRegistry(
        _seconds(app.config.get("PERMANENT_SESSION_LIFETIME", 0))
    )
    app.extensions["allowed_origins"] = _allowed_origins(app)

    app.before_request(_cors_preflight)
    app.before_request(_enforce_session_timeout)
    app.before_request(_csrf_protect)
    app.after_request(_security_headers)

    app.context_processor(
        lambda: {
            "csrf_token": get_csrf_token,
            "session_timeout": int(app.config.get("SESSION_IDLE_TIMEOUT", 0) or 0),
            "session_warning": int(
                app.config.get("SESSION_WARNING_SECONDS", 120) or 0
            ),
        }
    )
