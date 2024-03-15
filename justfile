@lint:
  echo mypy
  just --justfile {{justfile()}} mypy
  echo ruff
  just --justfile {{justfile()}} ruff
  echo ruff-format
  just --justfile {{justfile()}} ruff-format

@mypy:
  poetry run mypy .

@ruff:
  poetry run ruff check .

@ruff-format:
  poetry run ruff format meilisearch_tui tests

@install:
  poetry install

@test: start-meilisearch-detached && stop-meilisearch
  -poetry run pytest

@start-meilisearch:
  docker compose up

@start-meilisearch-detached:
  docker compose up -d


@start-meilisearch-hybrid-detached:
  docker compose up -d
  echo Enabling vector search
  curl \
    -X PATCH 'http://127.0.0.1:7700/experimental-features' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer masterKey' \
    --data-binary '{"vectorStore": true}'

@stop-meilisearch:
  docker compose down

@dev-cli:
  textual console

@dev: start-meilisearch-detached && stop-meilisearch
  -textual run --dev -c meilisearch

@dev-with-data: start-meilisearch-detached && stop-meilisearch
  echo Loading data
  poetry run python scripts/load_data.py
  echo Loading data successful, starting TUI
  -textual run --dev -c meilisearch

@dev-with-data-hybrid: start-meilisearch-hybrid-detached && stop-meilisearch
  echo Loading data
  poetry run python scripts/load_data.py
  echo Loading data successful, starting TUI
  -textual run --dev -c meilisearch -h
