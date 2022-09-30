# FOSS News Makefile
#
# Requirements:
# - Bash
# - sed
# - Docker
# - Docker Compose
# - container-diff (https://github.com/GoogleContainerTools/container-diff)
# - jq (https://stedolan.github.io/jq/)
# - yq (https://mikefarah.gitbook.io/yq/)

SHELL := /bin/bash

PROJECT := fossnews

# Python virtual environment
XDG_DATA_HOME ?= $(HOME)/.local/share
VENV ?= $(XDG_DATA_HOME)/venv/$(PROJECT)
ACTIVATE := . '$(VENV)/bin/activate'

# Docker, Compose, Django Admin commands
COMPOSE := docker compose
MANAGE_LOCAL := python manage.py
MANAGE_CONTAINER := $(COMPOSE) exec $(PROJECT) $(MANAGE_LOCAL)
BASE_IMAGE_TAG != sed -En '/ as app$$/s/^FROM +([^ ]+) +as +app$$/\1/p' Dockerfile
IMAGE_TAG != yq '.services.$(PROJECT).image' compose.yml
DIFF_FILE := $(PROJECT)-image.diff

# DB commands
define CHECK_DB :=
if $(COMPOSE) ps --format=json | \
jq --exit-status 'map(select(.Project == "$(PROJECT)" and .Service == "db")) == []' >/dev/null; \
then echo 'error: DB service is not running. Start it with `make db`.' >&2; exit 1; fi
endef
DB_TASK := $(CHECK_DB) && $(ACTIVATE) && DJANGO_DATABASE_HOST='localhost' $(MANAGE_LOCAL)
DB_VOLUME != yq '.services.db.volumes[0]|split(":")|"$(PROJECT)_"+.[0]' compose.yml

# Django superuser
ADMIN_NAME  ?= admin
ADMIN_EMAIL ?= admin@permlug.org

# Parameters for Make targets
name ?=
no_cache ?= 0

# Django settings for Django Admin commands
export DJANGO_SETTINGS_MODULE := $(PROJECT).settings

.PHONY: all venv touch-venv app lf                          # Development environment
.PHONY: build diff up down restart                          # Images, containers and services
.PHONY: db migrations showmigrations migrate admin sources  # DB and migrations
.PHONY: $(addprefix clean-,venv diff image db migrations)   # Cleaning

all: up

venv: $(VENV)
$(VENV): requirements.txt
	@python -m venv '$@' && $(ACTIVATE) && \
	pip install -U pip && pip install -r '$<'

touch-venv:
	@if [[ -d '$(VENV)' ]]; then touch '$(VENV)'; fi

app: fossnews/$(name)
	@:$(if $(name),,$(error missing app name))

fossnews/%: | venv
	@$(ACTIVATE) && cd fossnews && $(MANAGE) startapp '$(name)'

lf:
	@git ls-files --cached --others --exclude-per-directory=.gitignore -z \
	| xargs -0 file | sed -En '/with CRLF line terminators/s/^([^:]+):.*$/\1/p' | xargs dos2unix

build: Dockerfile nginx/Dockerfile
	@$(COMPOSE) build$(if $(no_cache:0=), --no-cache)

diff: $(DIFF_FILE)
$(DIFF_FILE):
	@docker pull '$(BASE_IMAGE_TAG)' && \
	container-diff diff 'daemon://$(BASE_IMAGE_TAG)' 'daemon://$(IMAGE_TAG)' --type=file --type=size > $@

up: compose.yml
	@$(COMPOSE) $@ -d

down restart: compose.yml
	@$(COMPOSE) $@

db: compose.yml
	@$(COMPOSE) up -d $@

migrations: | $(VENV)
	@$(DB_TASK) makemigrations

showmigrations migrate: | $(VENV)
	@$(DB_TASK) $@

admin:
	@$(DB_TASK) createsuperuser --username '$(ADMIN_NAME)' --email '$(ADMIN_EMAIL)'

sources: fossnews/gatherer/fixtures/sources.yaml
	@$(DB_TASK) loaddata $(notdir $<)

clean-venv:
	@-rm -rf '$(VENV)'

clean-image:
	@-docker image rm '$(IMAGE_TAG)'

clean-diff:
	@-rm -fv '$(DIFF_FILE)'

clean-db:
	@-docker volume rm '$(DB_VOLUME)'

clean-migrations:
	@-rm -fv fossnews/*/migrations/????_*.py
