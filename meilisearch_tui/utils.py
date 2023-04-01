from __future__ import annotations

from meilisearch_tui.client import get_client


async def get_current_indexes_string() -> str:
    async with get_client() as client:
        indexes = await client.get_indexes()

    if indexes:
        index_info = ""
        for index in indexes:
            if index.primary_key:
                index_info += f"Index UID: {index.uid}\nPrimary Key: {index.primary_key}\n\n"
            else:
                index_info += f"Index UID: {index.uid}\n\n"
    else:
        index_info = "No indexes available"

    return index_info
