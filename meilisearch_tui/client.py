from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from meilisearch_python_sdk import AsyncClient

from meilisearch_tui.config import load_config
from meilisearch_tui.errors import NoMeilisearchUrlError


@asynccontextmanager
async def get_client() -> AsyncGenerator[AsyncClient, None]:
    config = load_config()
    if not config.meilisearch_url:
        raise NoMeilisearchUrlError("No Meilisearch URL provided")

    client = AsyncClient(config.meilisearch_url, config.master_key)
    try:
        yield client
    finally:
        await client.aclose()
