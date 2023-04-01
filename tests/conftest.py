import json
from unittest.mock import patch

import pytest

from meilisearch_tui.config import Config, load_config


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


@pytest.fixture
def mock_config_dir(tmp_path):
    config_path = tmp_path / "config" / "meilisearch-tui"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    with patch.object(Config, "get_default_directory", return_value=config_path):
        yield config_path


@pytest.fixture
def mock_config(mock_config_dir):
    config = {
        "meilisearch_url": "http://127.0.0.1:7700",
        "master_key": "masterKey",
        "theme": "dark",
    }

    with open(mock_config_dir / "settings.json", "w") as f:
        json.dump(config, f)

    return load_config()
