#!/bin/sh
set -eu

exec celery --app fossnews worker --loglevel "$CELERY_LOG_LEVEL" --hostname "worker${1:-1}@%%h"
