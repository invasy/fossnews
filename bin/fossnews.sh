#!/bin/sh
set -eu

python manage.py collectstatic --clear --no-input

exec gunicorn fossnews.asgi:application \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "$DJANGO_HOST:$DJANGO_PORT"
