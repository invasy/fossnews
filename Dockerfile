FROM python:3.10-slim-bullseye as build
#
# Build django-celery-beat package with relaxed Django requirement:
#   `Django>=3.2,<4.1` -> `Django>=3.2,<4.2`.
# This stage can be removed after the next official release.
#
# See also:
# - https://github.com/celery/django-celery-beat/issues/566
# - https://github.com/celery/django-celery-beat/pull/567
#
RUN set -eu;\
    export DEBIAN_FRONTEND='noninteractive';\
    apt-get update -qq; apt-get upgrade -qq;\
    apt-get install -qqy --no-install-recommends git;\
    git clone --branch master --single-branch 'https://github.com/celery/django-celery-beat.git' /tmp/beat;\
    cd /tmp/beat;\
    sed -E '/^Django/s/(<4\.)1$/\12/' -i requirements/runtime.txt;\
    python setup.py bdist_wheel;\
    rm -rf /var/cache/* /var/log/* /var/lib/apt/lists/*


FROM python:3.10-slim-bullseye as app

ENV DJANGO_PORT=8000 DJANGO_ROOT="/srv/fossnews"
ENV DJANGO_STATIC_ROOT="$DJANGO_ROOT/static" \
    PATH="$DJANGO_ROOT/bin:/home/fossnews/.local/bin:$PATH" \
    PYTHONPATH="$DJANGO_ROOT" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Upgrade all packages and install AMQP client library (written in C)
RUN set -eu;\
    export DEBIAN_FRONTEND='noninteractive';\
    apt-get update -qq; apt-get upgrade -qq;\
    apt-get install -qqy --no-install-recommends librabbitmq4;\
    rm -rf /var/cache/* /var/log/* /var/lib/apt/lists/*

# Create fossnews user and group
RUN set -eu;\
    useradd --create-home --comment="FOSS News" --user-group fossnews;\
    yes fossnews | passwd fossnews
USER fossnews
WORKDIR "$DJANGO_ROOT"

# Install required Python packages
COPY --chown=fossnews:fossnews requirements.txt ./
COPY --chown=fossnews:fossnews --from=build /tmp/beat/dist/django_celery_beat-*.whl /tmp/
RUN set -eu;\
    pip_args='--user --no-cache-dir --no-compile';\
    pip_install="pip install $pip_args";\
    $pip_install --upgrade pip;\
    $pip_install /tmp/django_celery_beat-*.whl;\
    $pip_install --requirement=requirements.txt;\
    find "$HOME/.local/lib/python3.10/site-packages/" -type d -regextype posix-extended\
      -regex '.*/locale/[^/]+' -not -regex '.*/(en(_US)?|ru(_RU)?)' -exec rm -rf '{}' +;\
    for model in en_core_web_trf ru_core_news_lg; do\
      spacy download "$model" $pip_args;\
    done;\
    rm -rf /tmp/*

# Copy fossnews app
COPY --chown=fossnews:fossnews . ./
RUN set -eu;\
    chmod +x bin/* manage.py;\
    mkdir -p static

VOLUME "$DJANGO_STATIC_ROOT"
EXPOSE "$DJANGO_PORT"

ENTRYPOINT ["entrypoint.sh"]
CMD ["fossnews.sh"]
