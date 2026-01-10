#!/bin/sh
set -e

# simple wait-for-postgres loop
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
