@lint:
  echo black
  just --justfile {{justfile()}} black
  echo mypy
  just --justfile {{justfile()}} mypy
  echo ruff
  just --justfile {{justfile()}} ruff
  echo fmt

@black:
  poetry run black meilisearch_tui tests

@mypy:
  poetry run mypy .

@ruff:
  poetry run ruff check .

@install:
  poetry install

@test: start-meilisearch-detached && stop-meilisearch
  -poetry run pytest

@start-meilisearch:
  docker compose up

@start-meilisearch-detached:
  docker compose up -d

@stop-meilisearch:
  docker compose down

@dev-cli:
  textual console

@dev: start-meilisearch-detached && stop-meilisearch
  -textual run --dev meilisearch_tui/main.py

@dev-with-data: start-meilisearch-detached && stop-meilisearch
  echo Loading data
  poetry run python scripts/load_data.py
  echo Loading data successful, starting TUI
  -textual run --dev meilisearch_tui/main.py
