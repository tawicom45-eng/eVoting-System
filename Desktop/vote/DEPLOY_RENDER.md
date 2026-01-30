Render deployment notes — university_evoting

Quick checklist to deploy this project to Render (Docker):

- Build: This repo includes a production Dockerfile at the project root. Render will build the image using that Dockerfile.
- Start command: The Dockerfile sets a default CMD to run Gunicorn on port 8000. On Render use `$PORT` environment variable; the provided `render.yaml` sets a `startCommand` using `$PORT`.
- Entrypoint: `/entrypoint.sh` runs migrations/collectstatic; keep it executable and ensure it handles first-run DB migrations safely.

Required environment variables (add via Render Dashboard -> Environment):
- `SECRET_KEY` — Django secret
- `DATABASE_URL` — Postgres connection string (Render managed DB or external)
- `REDIS_URL` — if using Redis for Celery/Broker
- `DJANGO_SETTINGS_MODULE` — optional (default: `evoting_system.settings`)
- Email settings (SMTP): `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`
- Any 3rd-party credentials (SENTRY_DSN, CELERY_BROKER_URL aliasing to `REDIS_URL`, etc.)

Database & Redis:
- In Render, create a Managed PostgreSQL instance and attach it to the web and worker services (Render will provide `DATABASE_URL`).
- For Celery, provision a Redis instance (or use an external provider) and set `REDIS_URL`.

Note about `DATABASE_URL`:
- The project's `entrypoint.sh` now detects `DATABASE_URL` and parses it into `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` so the existing wait-for-postgres logic works on Render.

Worker process:
- The `render.yaml` includes a `worker` service which uses the same Dockerfile and runs `celery -A evoting_system worker -l info`. Add any required environment variables and attach the same `DATABASE_URL` and `REDIS_URL`.

Port & healthcheck:
- The Dockerfile exposes port 8000. Render provides a dynamic `PORT` env var — use the `startCommand` in `render.yaml` to bind Gunicorn to `$PORT`.

Static files:
- `entrypoint.sh` runs `collectstatic` — confirm it writes to a directory served by the app (or configure an external static host / S3 bucket for production).

Secrets and config guidance:
- Do NOT commit secrets to the repo. Use Render Environment settings.
- Set `ALLOWED_HOSTS` to include the Render service URL (or use `ALLOWED_HOSTS="*"` for initial testing, then tighten).

Optional improvements before production:
- Add a small `healthcheck` endpoint (e.g., `/health/`) for Render to monitor app readiness.
- Configure Gunicorn logging to write to stdout/stderr (already configured via command flags in Dockerfile).
- Add a readiness script to delay accepting traffic until migrations are applied and the DB is reachable.

Deploy steps (short):
1. Push repo to Git provider connected to Render.
2. Create a new Web Service using `render.yaml` or the Render UI (Docker). Attach Managed Postgres and provide `DATABASE_URL`.
3. Add environment variables listed above.
4. Create the Worker service and attach Redis via `REDIS_URL`.
5. Deploy; inspect logs for migrations and collectstatic output.

If you want, I can add a `Procfile`, a minimal healthcheck view, and a `start.sh` wrapper to gracefully wait for DB before running migrations.
