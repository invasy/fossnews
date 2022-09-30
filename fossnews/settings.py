"""
Django settings for fossnews project.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/

For the deployment checklist, see
https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
"""
import json
import os
import re
from os.path import expandvars
from pathlib import Path

from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _
from environ import Env


# Patch `Env` class to expand environment variables in settings values
setattr(Env, '_get_value', getattr(Env, 'get_value'))
setattr(Env, 'get_value', lambda self, *args, **kwargs: expandvars(self._get_value(*args, **kwargs)))


def emails_list(value: str) -> list[tuple[str, str]]:
    re_email = re.compile(r'^(?P<name>.+?) <(?P<email>[^>]+)>$')
    return [re_email.fullmatch(v).group('name', 'email') for v in re.split(r',\s*', value)]


####  Load settings from environment variables  ########################################################################
# https://django-environ.readthedocs.io/en/latest/quickstart.html
env = Env(
    DJANGO_SECRET_KEY=str,
    DJANGO_DEBUG=(bool, False),
    DJANGO_LOG_LEVEL=(str, 'WARNING'),
    DJANGO_TIME_ZONE=(str, 'UTC'),
    DJANGO_ALLOWED_HOSTS=([str], ['.localhost', '127.0.0.1', '[::1]']),
    DJANGO_ORIGINS=([str], ['http://localhost:8000']),
    DJANGO_STATIC_ROOT=(str, 'static/'),
    DJANGO_DATABASE_URL=str,
    DJANGO_DATABASE_ENGINE=str,
    DJANGO_DATABASE_HOST=str,
    DJANGO_DATABASE_PORT=int,
    DJANGO_DATABASE_NAME=str,
    DJANGO_DATABASE_USER=str,
    DJANGO_DATABASE_PASSWORD=str,
    DJANGO_FROM_EMAIL=str,
    DJANGO_SERVER_EMAIL=str,
    DJANGO_ADMINS=emails_list,
    DJANGO_MANAGERS=emails_list,
)
env.read_env('.env')
env.prefix = 'DJANGO_'

####  Core settings  ###################################################################################################
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'dynamic_preferences',
    'dynamic_preferences.users',
    'rest_framework',
    'fossnews.gatherer',
    # 'fossnews.classifier',
    # 'fossnews.telegram_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dynamic_preferences.processors.global_preferences',
            ],
        },
    },
]

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env('ORIGINS')

WSGI_APPLICATION = 'fossnews.wsgi.application'
ROOT_URLCONF = 'fossnews.urls'
STATIC_ROOT = env('STATIC_ROOT')
STATIC_URL = 'static/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

####  Database  ########################################################################################################
DATABASES = {
    'default': env.db(),
}

for option in ['ENGINE', 'HOST', 'PORT', 'NAME', 'USER', 'PASSWORD']:
    var = f'DATABASE_{option}'
    if env.prefix + var in env:
        DATABASES['default'][option] = env(var)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

####  Logging  #########################################################################################################
# https://docs.djangoproject.com/en/4.1/topics/logging/
# https://docs.python.org/3/library/logging.html
# https://docs.python.org/3/library/logging.config.html
# https://docs.python.org/3/library/logging.handlers.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        '': {
            'level': env('LOG_LEVEL'),
            'handlers': ['console'],
            'propagate': False,
        },
        'fossnews.parser': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'docker',
        },
    },
    'formatters': {
        'docker': {
            'format': '%(asctime)s | %(levelname)-8s | %(name)s | '
                      '%(message)s (%(funcName)s() at %(pathname)s:%(lineno)d)',
        },
    },
}

####  Email  ###########################################################################################################
DEFAULT_FROM_EMAIL = env('FROM_EMAIL')
SERVER_EMAIL = env('SERVER_EMAIL')
ADMINS = env('ADMINS')
MANAGERS = env('MANAGERS')

####  Internationalization  ############################################################################################
# https://docs.djangoproject.com/en/4.1/topics/i18n/
USE_I18N = True
LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
]
USE_TZ = True
TIME_ZONE = env('TIME_ZONE')

####  Django Rest Framework  ###########################################################################################
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

####  Dynamic preferences  #############################################################################################
DYNAMIC_PREFERENCES = {
    'REGISTRY_MODULE': 'preferences',
    'SECTION_KEY_SEPARATOR': '.',
}

####  Celery  ##########################################################################################################
CELERY_TIMEZONE = env('TIME_ZONE')
CELERY_BROKER_URL = env('BROKER_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'daily_news_gathering': {
        'schedule': crontab(hour=2, minute=1),
        'task': 'gather',
        'kwargs': {  # Source filters
            'enabled': True,
            'type': 'rss',
        },
    },
}
