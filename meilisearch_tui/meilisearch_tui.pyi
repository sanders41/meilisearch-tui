from __future__ import annotations

from typing import Any

def search_markdown(
    processing_time_ms: int, estimated_total_hits: int | None, hits: list[dict[str, Any]] | None
) -> str: ...
def settings_markdown(index: str, results: dict[str, Any]) -> str: ...
