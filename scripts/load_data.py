from __future__ import annotations

import asyncio

from meilisearch_python_async import Client
from meilisearch_python_async.task import wait_for_task


async def main() -> int:
    async with Client("http://127.0.0.1:7700", "masterKey") as client:
        index = client.index("movies")
        result = await index.add_documents_from_file("datasets/small_movies.json")
        await wait_for_task(index.http_client, result.task_uid)

    return 0


if __name__ == "__main__":
    asyncio.run(main())
