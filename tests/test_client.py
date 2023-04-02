import pytest

from meilisearch_tui.client import get_client
from meilisearch_tui.errors import NoMeilisearchUrlError


async def test_get_client_no_config(mock_config):
    mock_config.meilisearch_url = None
    mock_config.save()
    with pytest.raises(NoMeilisearchUrlError):
        async with get_client():
            pass
