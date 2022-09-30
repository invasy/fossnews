FROM nginx

ENV DJANGO_ROOT="/srv/fossnews" DJANGO_PORT=8000
ENV DJANGO_STATIC_ROOT="$DJANGO_ROOT/static"

RUN rm /etc/nginx/conf.d/default.conf
COPY fossnews.conf.template /etc/nginx/templates/

VOLUME "$DJANGO_STATIC_ROOT"
EXPOSE "$DJANGO_PORT"
