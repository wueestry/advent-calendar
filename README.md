# Advent Calendar

A Flask Advent Calendar web application managed with [`uv`](https://docs.astral.sh/uv/), featuring username/password login protection and date-gated door pages identified by unique SUIDs.

The interface is in Swiss German (`de-CH`), including localized dates such as `4. Dezember 2026`.

## Features

- **Login Protection**: All calendar and door routes require signing in with `APP_USERNAME` and `APP_PASSWORD` (or `APP_PASSWORD_HASH`).
- **Security Hardening**: CSRF protection, login throttling, automatic idle logout, strict security headers (CSP, HSTS, frame protection), hardened session cookies, and a deny-by-default CORS policy.
- **SUID Door URLs**: Each of the 24 doors is served at `/door/<suid>` instead of sequential `/day/<n>` URLs.
- **Date Gating (Stays Unlocked)**: Door `N` unlocks on `December N` of `CALENDAR_YEAR` and remains unlocked on all subsequent dates.
- **Locked Door Redirect**: Visiting a locked door's `/door/<suid>` URL directly redirects back to `/` with a flash message showing when the door unlocks.
- **Debug Override (`ENABLE_DEBUG=True`)**: Setting `ENABLE_DEBUG=True` unlocks all 24 doors regardless of the current date.
- **Pictures & Videos in Doors**: Each `Door` in `src/advent_calendar/doors.py` supports optional `image`, `image_alt`, `video` (local files in `src/advent_calendar/media/` or external URLs), and `youtube_embed` fields. Local media files are served through `/door/<suid>/media/<filename>` behind the same login and date-unlock checks as the door itself.
- **Line Breaks in Door Content**: Use `\n` in a door's `content` string to add line breaks. The text is escaped first, so HTML in content stays plain text.
- **Fast, Lightweight UI**: A single small stylesheet, no JavaScript framework, immutable caching for versioned static assets, and animations limited to compositor-friendly properties.
- **Nerd Font Icons**: The bundled Symbols Nerd Font renders Nerd Font glyphs in door content, so private-use icon characters can be used directly in `doors.py` strings.


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

For a production deployment, set `APP_ENV=production`, a unique `SECRET_KEY`, a strong `APP_PASSWORD` (or `APP_PASSWORD_HASH`), and `COOKIE_SECURE=True`. Serve the app behind HTTPS; enable `TRUST_PROXY_HEADERS=True` only when a trusted reverse proxy sets `X-Forwarded-*` headers. The app refuses to start in production with the default secret or password.

The Docker image serves the app with Gunicorn, not the Flask development server. Without Docker, run it the same way:

```bash
# One worker keeps the in-memory login throttle shared across requests
uv run gunicorn --bind 0.0.0.0:5000 --worker-class gthread --workers 1 --threads 8 \
  "advent_calendar:create_app()"
```

Use `uv run flask --app advent_calendar run` only for local development.

## Configuration

Copy `.env.example` to `.env` or set environment variables directly:

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | `development` or `production`. Production rejects default secrets. | `development` |
| `SECRET_KEY` | Secret key for signing Flask session cookies | `dev-advent-calendar-secret-key` |
| `APP_USERNAME` | Login username | `admin` |
| `APP_PASSWORD` | Login password | `advent2026` |
| `APP_PASSWORD_HASH` | Optional Werkzeug password hash; takes precedence over `APP_PASSWORD` | empty |
| `ENABLE_DEBUG` | Unlock all doors regardless of date (`True`/`False`) | `False` |
| `CALENDAR_YEAR` | Year for the December 1–24 unlock schedule | Current year |
| `TIMEZONE` | IANA timezone name used to determine today's date | `Europe/Zurich` |
| `COOKIE_SECURE` | Mark the session cookie `Secure` (enable behind HTTPS) | `False` |
| `SESSION_LIFETIME_HOURS` | Absolute session lifetime | `12` |
| `SESSION_IDLE_TIMEOUT_MINUTES` | Automatic logout after inactivity (`0` disables) | `30` |
| `LOGIN_MAX_ATTEMPTS` | Failed logins before a temporary lockout | `5` |
| `LOGIN_LOCKOUT_SECONDS` | Duration of the login lockout | `900` |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowlist. Empty disables CORS headers. | empty |
| `TRUST_PROXY_HEADERS` | Trust `X-Forwarded-*` headers from one reverse proxy | `False` |
| `TRUSTED_HOSTS` | Optional comma-separated host allowlist | empty |

## Fonts

The UI bundles [Nerd Fonts Symbols Only](https://github.com/ryanoasis/nerd-fonts) `v3.5.1` as `src/advent_calendar/static/fonts/SymbolsNerdFont-Regular.woff2` (MIT licensed; see the [font license](src/advent_calendar/static/fonts/LICENSE)). It is used as a fallback for Nerd Font glyphs in door content. Thanks to `unicode-range`, browsers download the font only when a page contains one of its glyphs.

## Security

- All state-changing requests (`POST`) require a per-session CSRF token, including the login and logout forms.
- Failed logins are throttled per client address. The limiter is in-memory, so each application process keeps its own counter.
- Sessions are `HttpOnly` and `SameSite=Lax`, expire after an absolute lifetime, and are logged out automatically after the configured idle timeout. The UI warns before the idle timeout and offers to extend the session.
- Logout revokes the session nonce in process memory, so a captured session cookie cannot be replayed after logout or timeout. Because the registry is process-local, restarting the app logs everyone out and the app must run as a single process (the shipped Gunicorn config uses one worker) for revocation to be consistent.
- Responses send `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`, and `Cross-Origin-Resource-Policy`. HSTS is sent on every response; browsers only enforce it over HTTPS, so production must still be served over TLS (directly or via a trusted reverse proxy).
- CORS is deny-by-default. Only origins in `ALLOWED_ORIGINS` receive CORS headers.
- Static assets are versioned by modification time and cached immutably; HTML responses are never cached.
- In production (`APP_ENV=production`), the app refuses to start with the default secret key or default password. The Docker image runs Gunicorn as a non-root user.

## Running Tests

```bash
uv run pytest
```
