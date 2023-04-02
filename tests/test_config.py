from unittest.mock import patch

import pytest

from meilisearch_tui.config import Config, Theme, load_config


def test_load_config(mock_config, mock_config_dir):
    config = load_config(config_dir=mock_config_dir)
    assert config.__dict__ == mock_config.__dict__


@pytest.mark.usefixtures("mock_config")
def test_save_config(mock_config_dir):
    config = load_config(config_dir=mock_config_dir)
    config.meilisearch_url = "http://new"
    config.master_key = "new"
    config.theme = Theme.LIGHT
    config.timeout = 5
    config.save()
    updated = load_config(config_dir=mock_config_dir)
    assert updated.__dict__ == config.__dict__


def test_save_config_create_dir(tmp_path, mock_config_dir):
    config_path = tmp_path / "config" / "meilisearch-tui"

    with patch.object(Config, "get_default_directory", return_value=config_path):
        config = load_config(config_dir=mock_config_dir)
        config.save()

    assert config_path.exists() is True


@pytest.mark.usefixtures("mock_config")
def test_delete_config(mock_config_dir):
    config = load_config(config_dir=mock_config_dir)
    config.delete()
    settings_files = mock_config_dir / "settings.json"

    assert settings_files.exists() is False
