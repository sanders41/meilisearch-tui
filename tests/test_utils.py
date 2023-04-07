import pytest

from meilisearch_tui.utils import get_current_indexes_string, string_to_list


@pytest.mark.parametrize(
    "indexes, expected",
    [
        [[("movies", "movie_id")], "Index UID: movies\nPrimary Key: movie_id\n\n"],
        [
            [
                ("movies", "movie_id"),
                ("books", "book_id"),
            ],
            "Index UID: books\nPrimary Key: book_id\n\nIndex UID: movies\nPrimary Key: movie_id\n\n",
        ],
        [[("movies", None)], "Index UID: movies\n\n"],
    ],
)
@pytest.mark.usefixtures("clear_indexes", "mock_config", "env_vars")
async def test_get_current_indexes_string(indexes, expected, test_client):
    for index in indexes:
        await test_client.create_index(index[0], index[1])

    result = await get_current_indexes_string()

    assert result == expected


@pytest.mark.usefixtures("mock_config", "env_vars")
async def test_get_current_indexes_string_no_indexes():
    result = await get_current_indexes_string()

    assert result == "No indexes available"


@pytest.mark.parametrize(
    "val, expected",
    [
        ("['a', 'b']", ["a", "b"]),
        ('["a", "b"]', ["a", "b"]),
        ("[\"a', 'b']", ["a", "b"]),
        ('["title"]', ["title"]),
        ("[]", None),
        (None, None),
    ],
)
def test_string_to_list(val, expected):
    assert string_to_list(val) == expected
