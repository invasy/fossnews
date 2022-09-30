#!/bin/sh
set -eu

exec celery --app fossnews beat --loglevel "$CELERY_LOG_LEVEL"
