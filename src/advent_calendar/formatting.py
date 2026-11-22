from __future__ import annotations

from markupsafe import Markup, escape


def format_content(value: str) -> Markup:
    """Render plain-text door content, turning ``\\n`` into HTML line breaks.

    Each line is escaped before the lines are joined, so the returned markup is
    safe to render with ``|safe`` semantics.
    """
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return Markup("<br>\n").join(escape(line) for line in normalized.split("\n"))
