#!/usr/bin/env python
import sys

import psycopg2
from django.conf import settings


if __name__ == '__main__':
    try:
        conn = psycopg2.connect(
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            database=settings.DATABASES['default']['NAME'],
        )
        conn.close()

    except psycopg2.OperationalError:
        sys.exit(1)

    sys.exit(0)
