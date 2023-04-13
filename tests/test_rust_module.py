from _meilisearch_tui import search_markdown, settings_markdown


def test_search_markdown():
    result = search_markdown(
        estimated_total_hits=10,
        processing_time_ms=1,
        hits=[{"id": 1, "title": "Test 1"}, {"id": 2, "title": "Test 2"}],
    )

    assert (
        result
        == "## Hits: ~10 | Search time: 1\n\nid: 1\ntitle: Test 1\n-------------------------------\nid: 2\ntitle: Test 2\n-------------------------------"
    )


def test_settings_markdown():
    result = settings_markdown(
        "test-index", {"key_1": "value 1", "key_2": "value 2", "key_3": {}, "key_4": []}
    )

    assert (
        result
        == "# Settings for test-index index\n\n## Key 1\nvalue 1\n\n## Key 2\nvalue 2\n\n## Key 3\n{}\n\n## Key 4\n[]\n"
    )
