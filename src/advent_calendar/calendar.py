from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from advent_calendar.auth import login_required
from advent_calendar.config import DEFAULT_MEDIA_DIR, parse_bool
from advent_calendar.doors import DOORS, get_door_by_suid
from advent_calendar.i18n import format_date_de, format_day_month_de

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
    target_year = int(
        year
        if year is not None
        else current_app.config.get("CALENDAR_YEAR", date.today().year)
    )
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


def _locked_door_message(day: int, year: int) -> str:
    unlock_date = unlock_date_for_day(day, year=year)
    return (
        f"Tür Nr. {day} ist noch verschlossen! "
        f"Sie öffnet sich am {format_date_de(unlock_date)}."
    )


@calendar_bp.route("/")
@login_required
def index() -> Any:
    today = get_today()
    debug_active = is_debug_enabled()
    year = int(current_app.config.get("CALENDAR_YEAR", today.year))

    door_items = []
    for door in DOORS:
        unlock_date = unlock_date_for_day(door.day, year=year)
        door_items.append(
            {
                "door": door,
                "is_open": is_door_openable(
                    door.day,
                    today=today,
                    enable_debug=debug_active,
                    year=year,
                ),
                "unlock_date": unlock_date,
                "unlock_label": format_day_month_de(unlock_date),
            }
        )

    return render_template(
        "index.html",
        door_items=door_items,
        today_label=format_date_de(today),
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
        flash(_locked_door_message(door.day, year), "warning")
        return redirect(url_for("calendar.index"))

    return render_template(
        "door.html",
        door=door,
        image_url=resolve_door_media_url(door.suid, door.image),
        video_url=resolve_door_media_url(door.suid, door.video),
        calendar_year=year,
        debug_enabled=debug_active,
    )


def resolve_door_media_url(suid: str, media_ref: str | None) -> str | None:
    if not media_ref:
        return None
    if media_ref.startswith(("http://", "https://")):
        return media_ref
    return url_for("calendar.door_media", suid=suid, filename=media_ref)


@calendar_bp.route("/door/<string:suid>/media/<path:filename>")
@login_required
def door_media(suid: str, filename: str) -> Any:
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
        flash(_locked_door_message(door.day, year), "warning")
        return redirect(url_for("calendar.index"))

    allowed_files = {
        ref
        for ref in (door.image, door.video)
        if ref and not ref.startswith(("http://", "https://"))
    }
    if filename not in allowed_files:
        abort(404)

    media_dir = Path(current_app.config.get("MEDIA_DIR", DEFAULT_MEDIA_DIR))
    return send_from_directory(media_dir, filename)
