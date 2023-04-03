from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from meilisearch_tui.utils import get_current_indexes_string


class CurrentIndexes(Widget):
    DEFAULT_CSS = """
    CurrentIndexes {
        border: $primary;
        height: 25;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="current-indexes-view"):
            yield Static(id="current-indexes", expand=True)

    async def update(self) -> None:
        current_indexes = self.query_one("#current-indexes", Static)
        try:
            indexes = await get_current_indexes_string()
            current_indexes.update(indexes)
        except Exception as e:
            current_indexes.update(f"Error: {e}")
