# Advent Calendar

A Flask Advent Calendar web application managed with [`uv`](https://docs.astral.sh/uv/), featuring username/password login protection and date-gated door pages identified by unique SUIDs.

## Features

- **Login Protection**: All calendar and door routes require signing in with `APP_USERNAME` and `APP_PASSWORD`.
- **SUID Door URLs**: Each of the 24 doors is served at `/door/<suid>` instead of sequential `/day/<n>` URLs.
- **Date Gating (Stays Unlocked)**: Door `N` unlocks on `December N` of `CALENDAR_YEAR` and remains unlocked on all subsequent dates.
- **Locked Door Redirect**: Visiting a locked door's `/door/<suid>` URL directly redirects back to `/` with a flash message showing when the door unlocks.
- **Debug Override (`ENABLE_DEBUG=True`)**: Setting `ENABLE_DEBUG=True` unlocks all 24 doors regardless of the current date.

## Quickstart (`uv`)

```bash
# Run the Flask development server
uv run flask --app advent_calendar run

# Or run with all doors unlocked via ENABLE_DEBUG=True
ENABLE_DEBUG=True uv run flask --app advent_calendar run
```

## Running with Docker Compose

```bash
# Build and start on http://localhost:5000
docker compose up --build

# Or run with debug mode enabled (all doors unlocked)
ENABLE_DEBUG=True docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` or set environment variables directly:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Secret key for signing Flask session cookies | `dev-advent-calendar-secret-key` |
| `APP_USERNAME` | Login username | `admin` |
| `APP_PASSWORD` | Login password | `advent2026` |
| `ENABLE_DEBUG` | Unlock all doors regardless of date (`True`/`False`) | `False` |
| `CALENDAR_YEAR` | Year for the December 1–24 unlock schedule | Current year |
| `TIMEZONE` | IANA timezone name used to determine today's date | `UTC` |

## Running Tests

```bash
uv run pytest
```
