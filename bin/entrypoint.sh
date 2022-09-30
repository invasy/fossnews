#!/bin/sh
set -eu

until postgres-ready.py; do
  echo 'Waiting for PostgreSQL server...' >&2
  sleep 1
done

python manage.py migrate

exec "$@"
