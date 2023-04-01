from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from meilisearch_python_async import Client

from meilisearch_tui.config import config
from meilisearch_tui.errors import NoMeilisearchUrlError


@asynccontextmanager
async def get_client() -> AsyncGenerator[Client, None]:
    if not config.meilisearch_url:
        raise NoMeilisearchUrlError("No Meilisearch URL provided")

    client = Client(config.meilisearch_url, config.master_key)
    try:
        yield client
    finally:
        await client.aclose()
