from __future__ import annotations

import asyncio

from meilisearch_python_async.errors import MeilisearchCommunicationError
from meilisearch_python_async.models.search import SearchResults
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container, Content
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Markdown

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.messages import ErrorMessage


class SearchScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.limit = 20

    def compose(self) -> ComposeResult:
        yield ErrorMessage("", classes="message-centered", id="generic_error")
        with Container(id="body"):
            yield Input(placeholder="Index", classes="bottom-spacer", id="index_name")
            yield Input(placeholder="Search", classes="bottom-spacer", id="search")
            with Content(id="results-container"):
                yield Markdown(id="results")
            with Center():
                yield Button(label="Load More", classes="bottom-spacer", id="load_more_button")
        yield Footer()

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        body_container = self.query_one("#body")
        error_message = self.query_one("#generic_error")
        body_container.visible = True
        error_message.display = False
        index_name = self.query_one("#index_name", Input)
        search = self.query_one("#search", Input)
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError as e:
            body_container.visible = False
            error_message.display = True
            error_message.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"
            return
        except Exception as e:
            body_container.visible = False
            error_message.display = True
            error_message.renderable = f"An error occured: {e}."
            return

        if indexes:
            index_name.value = indexes[0].uid

        search.focus()
        self.query_one("#load_more_button", Button).visible = False

    async def on_input_changed(self, message: Input.Changed) -> None:
        self.limit = 20
        if message.value:
            asyncio.create_task(self.lookup_word(message.value))
        else:
            await self.query_one("#results", Markdown).update("")
            self.query_one("#load_more_button", Button).visible = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "load_more_button":
            self.limit += 20
            asyncio.create_task(self.lookup_word(self.query_one("#search", Input).value))

    async def lookup_word(self, search: str) -> None:
        index_name = self.query_one("#index_name", Input).value
        results_box = self.query_one("#results", Markdown)
        search_input = self.query_one("#search", Input)
        if not index_name and search == search_input.value:
            await results_box.update("Error: No index provided")
            return

        async with get_client() as client:
            index = client.index(index_name)
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
            self.query_one("#load_more_button", Button).visible = True
        else:
            self.query_one("#load_more_button", Button).visible = False

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
