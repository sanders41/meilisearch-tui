from __future__ import annotations

import asyncio

from meilisearch_python_sdk import AsyncClient


async def main() -> int:
    async with AsyncClient("http://127.0.0.1:7700", "masterKey") as client:
        index = client.index("movies")
        result = await index.add_documents_from_file("datasets/small_movies.json")
        await client.wait_for_task(result.task_uid)

    return 0


if __name__ == "__main__":
    asyncio.run(main())
