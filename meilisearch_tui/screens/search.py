from __future__ import annotations

import asyncio

from meilisearch_python_async.errors import MeilisearchCommunicationError
from meilisearch_python_async.models.search import SearchResults
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container, Content
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Markdown, Static

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.messages import ErrorMessage


class SearchScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.limit = 20
        self.selected_index: str | None = None

    def compose(self) -> ComposeResult:
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            yield Static("No index selected", id="index-name", classes="bottom-spacer")
            yield Input(placeholder="Search", classes="bottom-spacer", id="search")
            with Content(id="results-container"):
                yield Markdown(id="results")
            with Center():
                yield Button(label="Load More", classes="bottom-spacer", id="load-more-button")
        yield Footer()

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        body_container = self.query_one("#body")
        error_message = self.query_one("#generic-error")
        body_container.visible = True
        error_message.display = False
        index_name = self.query_one("#index-name", Static)
        index_sidebar = self.query_one(IndexSidebar)
        await index_sidebar.update()
        search = self.query_one("#search", Input)
        search.value = ""
        await self.query_one("#results", Markdown).update("")
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError as e:
            body_container.visible = False
            error_message.display = True
            error_message.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"  # type: ignore
            return
        except Exception as e:
            body_container.visible = False
            error_message.display = True
            error_message.renderable = f"An error occured: {e}."  # type: ignore
            return

        if indexes:
            index_name.update(f"Searching index: {indexes[0].uid}")
            self.selected_index = index_sidebar.selected_index
        else:
            self.selected_index = None
            self.query_one("#index-name", Static).update("No index selected")

        search.focus()
        self.query_one("#load-more-button", Button).visible = False

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        index_sidebar = self.query_one(IndexSidebar)
        self.selected_index = index_sidebar.selected_index
        self.query_one("#index-name", Static).update(f"Searching index: {self.selected_index}")
        self.query_one("#search", Input).value = ""
        await self.query_one("#results", Markdown).update("")

    async def on_input_changed(self, message: Input.Changed) -> None:
        self.limit = 20
        if message.value:
            asyncio.create_task(self.lookup_word(message.value))
        else:
            await self.query_one("#results", Markdown).update("")
            self.query_one("#load-more-button", Button).visible = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "load-more-button":
            self.limit += 20
            asyncio.create_task(self.lookup_word(self.query_one("#search", Input).value))

    async def lookup_word(self, search: str) -> None:
        results_box = self.query_one("#results", Markdown)
        search_input = self.query_one("#search", Input)
        if not self.selected_index and search == search_input.value:
            await results_box.update("Error: No index provided")
            return

        if not self.selected_index:
            await results_box.update("No index selected")
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            try:
                results = await index.search(search_input.value, limit=self.limit)
            except Exception as e:
                if search == search_input.value:
                    await results_box.update(f"Error: {e}")
                return

        # Make sure a new search hasn't started. This prevents race conditions with displaying
        # the search results by only updating the display if the search is still relavent.
        if search == search_input.value:
            markdown = self.make_word_markdown(results)
            await results_box.update(markdown)

    def make_word_markdown(self, results: SearchResults) -> str:
        lines = []

        if results.estimated_total_hits and results.estimated_total_hits > len(results.hits):
            self.query_one("#load-more-button", Button).visible = True
        else:
            self.query_one("#load-more-button", Button).visible = False

        lines.append(
            f"## Hits: ~{results.estimated_total_hits} | Search time: {results.processing_time_ms} ms"
        )

        if results.hits:
            for hit in results.hits:
                for k, v in hit.items():
                    lines.append(f"{k}: {v}\n")
                lines.append("-------------------------------")
            return "\n".join(lines)

        return "No results found"
