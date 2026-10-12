.PHONY: up down build logs shell test test-cov lint seed import clean

up:
\tdocker compose up --build -d

down:
\tdocker compose down

build:
\tdocker compose build

logs:
\tdocker compose logs -f app

shell:
\tdocker compose exec app bash

test:
\tdocker compose exec app pytest -v

test-cov:
\tdocker compose exec app pytest --cov=app --cov-report=term-missing

lint:
\tdocker compose exec app ruff check app tests

seed:
\tdocker compose exec app python -m app.scripts.seed_categories

import:
\t@test -n "$(FILE)" || (echo "Usage: make import FILE=path/to/file.csv" && exit 1)
\tdocker compose exec app python -m app.scripts.import_csv /data/$(FILE)

clean:
\tdocker compose down -v
