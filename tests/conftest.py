import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from meilisearch_python_sdk import AsyncClient

from meilisearch_tui.config import Config, load_config

BASE_URL = "http://127.0.0.1:7700"
MASTER_KEY = "masterKey"


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
async def test_client():
    async with AsyncClient(BASE_URL, MASTER_KEY) as client:
        yield client


@pytest.fixture
async def clear_indexes(test_client):
    yield
    indexes = await test_client.get_indexes()
    if indexes:
        for index in indexes:
            response = await test_client.index(index.uid).delete()
            await test_client.wait_for_task(response.task_uid)


@pytest.fixture
async def load_test_movie_data(test_client):
    root_path = Path().absolute()
    index = test_client.index("movies")
    result = await index.add_documents_from_file(root_path / "datasets" / "small_movies.json")
    await test_client.wait_for_task(result.task_uid)
    yield
    indexes = await test_client.get_indexes()
    if indexes:
        for index in indexes:
            response = await test_client.index(index.uid).delete()
            await test_client.wait_for_task(response.task_uid)
