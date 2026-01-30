#!/bin/sh
set -e

# simple wait-for-postgres loop
# If running on Render (or other hosts) the DB may be provided as DATABASE_URL.
# Parse it into POSTGRES_* env vars so the existing wait logic works.
if [ -n "$DATABASE_URL" ]; then
  echo "Parsing DATABASE_URL into POSTGRES_* variables..."
  eval "$(python - <<'PY'
import os
from urllib.parse import urlparse
url = os.environ.get('DATABASE_URL')
if not url:
    raise SystemExit(0)
p = urlparse(url)
user = p.username or ''
password = p.password or ''
host = p.hostname or ''
port = p.port or ''
path = p.path[1:] if p.path and p.path.startswith('/') else p.path or ''
print(f"export POSTGRES_HOST='{host}'")
print(f"export POSTGRES_PORT='{port}'")
print(f"export POSTGRES_DB='{path}'")
print(f"export POSTGRES_USER='{user}'")
print(f"export POSTGRES_PASSWORD='{password}'")
PY
  )"
fi

host="$POSTGRES_HOST"
port="$POSTGRES_PORT"
user="$POSTGRES_USER"
password="$POSTGRES_PASSWORD"

if [ -n "$host" ]; then
  echo "Waiting for postgres at ${host}:${port:-5432}..."
  until python - <<PY > /dev/null 2>&1
import time
import os
import psycopg2
try:
    dsn = dict(dbname=os.environ.get('POSTGRES_DB'), user=os.environ.get('POSTGRES_USER'), password=os.environ.get('POSTGRES_PASSWORD'), host=os.environ.get('POSTGRES_HOST'), port=os.environ.get('POSTGRES_PORT','5432'))
    psycopg2.connect(**dsn).close()
    print('ok')
except Exception:
    raise SystemExit(1)
PY
  do
    echo "Postgres is unavailable - sleeping"
    sleep 1
  done
fi

# Apply migrations and collect static then run the command
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Execute the command passed to the container
exec "$@"
