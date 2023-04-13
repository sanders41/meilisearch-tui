from __future__ import annotations

from typing import Any

__all__ = ("search_markdown", "settings_markdown")

def search_markdown(
    estimated_total_hits: int, processing_time_ms: int, hits: list[dict[str, Any]] | None
) -> str: ...
def settings_markdown(index: str, results: dict[str, Any]) -> str: ...
