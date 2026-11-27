# Advent Calendar

A Flask advent calendar web application with username/password protection, date-gated doors, and Nerd Font icons.

## Quickstart

```bash
# Development
uv run flask --app advent_calendar run

# With all doors unlocked
ENABLE_DEBUG=True uv run flask --app advent_calendar run

# Docker
docker compose up --build

# With debug mode
ENABLE_DEBUG=True docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` or set environment variables:

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `production` rejects defaults |
| `SECRET_KEY` | `dev-advent-calendar-secret-key` | Session signing key |
| `APP_USERNAME` | `admin` | Login username |
| `APP_PASSWORD` | `advent2026` | Login password |
| `ENABLE_DEBUG` | `False` | Unlock all doors |
| `CALENDAR_YEAR` | current year | Unlock schedule year |
| `TIMEZONE` | `Europe/Zurich` | Date determination timezone |
| `COOKIE_SECURE` | `False` | Secure session cookie |
| `SESSION_LIFETIME_HOURS` | `12` | Session lifetime |
| `SESSION_IDLE_TIMEOUT_MINUTES` | `30` | Idle logout timeout |
| `LOGIN_MAX_ATTEMPTS` | `5` | Failed login attempts before lockout |
| `LOGIN_LOCKOUT_SECONDS` | `900` | Lockout duration |
| `TRUST_PROXY_HEADERS` | `False` | Trust `X-Forwarded-*` headers |

## Security

- CSRF protection on all state-changing requests
- Login throttling per client address
- HttpOnly, SameSite=Lax session cookies with configurable lifetime
- Automatic logout after idle timeout
- Security headers: CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, COOP, COEP
- Deny-by-default CORS; only whitelisted origins receive headers
- Static assets versioned by modification time, cached immutably
- Production refuses default secret key or password

## Running Tests

```bash
uv run pytest
```