from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)

from advent_calendar.auth import login_required
from advent_calendar.config import parse_bool
from advent_calendar.doors import DOORS, get_door_by_suid

calendar_bp = Blueprint("calendar", __name__)


def get_today() -> date:
    configured_date = current_app.config.get("CURRENT_DATE")
    if isinstance(configured_date, date):
        return configured_date
    if isinstance(configured_date, str) and configured_date:
        return date.fromisoformat(configured_date)

    tz_name = str(current_app.config.get("TIMEZONE", "UTC"))
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    return datetime.now(tz).date()


def is_debug_enabled() -> bool:
    if "ENABLE_DEBUG" in current_app.config:
        cfg_val = parse_bool(current_app.config["ENABLE_DEBUG"])
        if cfg_val:
            return True
    env_val = os.environ.get("ENABLE_DEBUG")
    if env_val is not None:
        return parse_bool(env_val)
    return False


def unlock_date_for_day(day: int, year: int | None = None) -> date:
    target_year = int(year if year is not None else current_app.config.get("CALENDAR_YEAR", date.today().year))
    return date(target_year, 12, day)


def is_door_openable(
    day: int,
    *,
    today: date | None = None,
    enable_debug: bool | None = None,
    year: int | None = None,
) -> bool:
    if not 1 <= day <= 24:
        return False

    debug_active = is_debug_enabled() if enable_debug is None else enable_debug
    if debug_active:
        return True

    current_day = today if today is not None else get_today()
    unlock_date = unlock_date_for_day(day, year=year)
    return current_day >= unlock_date


@calendar_bp.route("/")
@login_required
def index() -> Any:
    today = get_today()
    debug_active = is_debug_enabled()
    year = int(current_app.config.get("CALENDAR_YEAR", today.year))

    door_items = [
        {
            "door": door,
            "is_open": is_door_openable(
                door.day,
                today=today,
                enable_debug=debug_active,
                year=year,
            ),
            "unlock_date": unlock_date_for_day(door.day, year=year),
        }
        for door in DOORS
    ]

    return render_template(
        "index.html",
        door_items=door_items,
        today=today,
        calendar_year=year,
        debug_enabled=debug_active,
    )


@calendar_bp.route("/door/<string:suid>")
@login_required
def door_detail(suid: str) -> Any:
    door = get_door_by_suid(suid)
    if door is None:
        abort(404)

    today = get_today()
    debug_active = is_debug_enabled()
    year = int(current_app.config.get("CALENDAR_YEAR", today.year))

    if not is_door_openable(
        door.day,
        today=today,
        enable_debug=debug_active,
        year=year,
    ):
        unlock_date = unlock_date_for_day(door.day, year=year)
        flash(
            f"Door #{door.day} is still locked! It opens on {unlock_date.strftime('%B %-d, %Y')}.",
            "warning",
        )
        return redirect(url_for("calendar.index"))

    return render_template(
        "door.html",
        door=door,
        today=today,
        calendar_year=year,
        debug_enabled=debug_active,
    )
