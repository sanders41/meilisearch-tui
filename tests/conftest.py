import asyncio
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from meilisearch_tui.config import Config, load_config

BASE_URL = "http://127.0.0.1:7700"
MASTER_KEY = "masterKey"


@pytest.fixture
async def clear_indexes(async_client):
    yield
    indexes = await async_client.get_indexes()
    if indexes:
        for index in indexes:
            response = await async_client.index(index.uid).delete()
            await async_client.wait_for_task(response.task_uid)


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def clear_lru_cache():
    yield
    load_config.cache_clear()


@pytest.fixture(autouse=True, scope="session")
def dont_write_to_home_config_directory():
    """Makes sure a default directory is specified for config so that the home directory is not
    written to in testing.
    """

    class ExplicitlyChooseCacheDirectory(AssertionError):
        pass

    with patch.object(
        Config,
        "get_default_directory",
        side_effect=ExplicitlyChooseCacheDirectory,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_config_dir(tmp_path):
    config_path = tmp_path / "config" / "meilisearch-tui"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    with patch.object(Config, "get_default_directory", return_value=config_path):
        yield config_path


@pytest.fixture
def mock_config(mock_config_dir):
    config = {
        "meilisearch_url": BASE_URL,
        "master_key": MASTER_KEY,
        "theme": "dark",
    }

    with open(mock_config_dir / "settings.json", "w") as f:
        json.dump(config, f)

    return load_config(config_dir=mock_config_dir)


@pytest.fixture
def env_vars():
    with patch.dict(
        os.environ,
        {"MEILI_HTTP_ADDR": "http://127.0.0.1:7700", "MEILI_MASTER_KEY": "masterKey"},
        clear=True,
    ):
        yield


@pytest.fixture
async def load_test_movie_data(async_client):
    root_path = Path().absolute()
    index = async_client.index("movies")
    result = await index.add_documents_from_file(root_path / "datasets" / "small_movies.json")
    await async_client.wait_for_task(result.task_uid)
    yield
