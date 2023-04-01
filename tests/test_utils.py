import pytest

from meilisearch_tui.utils import get_current_indexes_string


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
@pytest.mark.usefixtures("clear_indexes")
async def test_get_current_indexes_string(indexes, expected, test_client):
    for index in indexes:
        await test_client.create_index(index[0], index[1])

    result = await get_current_indexes_string()

    assert result == expected


async def test_get_current_indexes_string_no_indexes():
    result = await get_current_indexes_string()

    assert result == "No indexes available"
