from __future__ import annotations

from datetime import date

MONTHS_DE = (
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)

MONTHS_DE_SHORT = (
    "Jan.",
    "Feb.",
    "März",
    "Apr.",
    "Mai",
    "Juni",
    "Juli",
    "Aug.",
    "Sept.",
    "Okt.",
    "Nov.",
    "Dez.",
)


def format_date_de(value: date, *, short_month: bool = False) -> str:
    """Format a date in Swiss German style, for example ``4. Dezember 2026``."""
    months = MONTHS_DE_SHORT if short_month else MONTHS_DE
    return f"{value.day}. {months[value.month - 1]} {value.year}"


def format_day_month_de(value: date) -> str:
    """Format a date without the year, for example ``4. Dezember``."""
    return f"{value.day}. {MONTHS_DE[value.month - 1]}"
