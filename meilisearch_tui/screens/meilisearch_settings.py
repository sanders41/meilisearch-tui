from __future__ import annotations

import asyncio

from meilisearch_python_async.models.settings import (
    MeilisearchSettings as MeilisearchSettingsResult,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Content
from textual.screen import Screen
from textual.widgets import Footer, Markdown

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.messages import ErrorMessage


class MeilisearchSettings(Screen):
    def __init__(self, *, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.selected_index: str | None = None

    def compose(self) -> ComposeResult:
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            with Content(id="results-container"):
                yield Markdown(id="results")
        yield Footer()

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        body_container = self.query_one("#body", Container)
        error_message = self.query_one("#generic-error", ErrorMessage)
        body_container.visible = True
        error_message.display = False
        index_sidebar = self.query_one(IndexSidebar)
        await index_sidebar.update()
        self.selected_index = index_sidebar.selected_index
        asyncio.create_task(self.load_indexes())

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        index_sidebar = self.query_one(IndexSidebar)
        self.selected_index = index_sidebar.selected_index
        asyncio.create_task(self.load_indexes())

    async def load_indexes(self) -> None:
        # save the selected index at the start to make sure it hasn't changed during the request
        current_index = self.selected_index
        results_box = self.query_one("#results", Markdown)

        if not self.selected_index:
            results_box.update("No index selected")
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            try:
                results = await index.get_settings()
            except Exception as e:
                if current_index == self.selected_index:
                    results_box.update(f"Error: {e}")
                return

        if current_index == self.selected_index:
            markdown = self.make_word_markdown(current_index, results)
            results_box.update(markdown)

    def make_word_markdown(self, index: str, results: MeilisearchSettingsResult) -> str:
        lines = []

        lines.append(f"# Settigns for {index} index")

        for k, v in results.dict().items():
            lines.append(f"## {k}\n{v}\n")

        return "\n".join(lines)
