# FOSS News

## Requirements
- Docker
- Docker Compose

## Powered By
- Python 3.10
- aiohttp
- Django 4.1
- spaCy
- Docker
- Docker Compose

## Production
- Start all services:
    ```shell
    make
    ```
- Stop all services:
    ```shell
    make down
    ```

## Development
- Make Python virtual environment:
    ```shell
    make venv
    ```
- Remove DB, remove all migrations and make them from scratch:
    ```shell
    make down clean-migrations clean-db
    make db
    sleep 2  # Wait for DB server to start
    make migrations migrate admin build
    ```
- Build images without cache:
    ```shell
    make build no_cache=1
    ```
- Restart services with modified app:
    ```shell
   make down build up
    ```
