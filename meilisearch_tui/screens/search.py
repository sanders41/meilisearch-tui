from __future__ import annotations

import asyncio

from meilisearch_python_async.models.search import SearchResults
from textual.app import ComposeResult
from textual.containers import Center, Container, Content
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Markdown

from meilisearch_tui.client import get_client


class SearchScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.limit = 20

    def compose(self) -> ComposeResult:
        with Container(id="body"):
            yield Input(placeholder="Index", classes="bottom-spacer", id="index_name")
            yield Input(placeholder="Search", classes="bottom-spacer", id="search")
            with Content(id="results-container"):
                yield Markdown(id="results")
            with Center():
                yield Button(label="Load More", classes="bottom-spacer", id="load_more_button")
        yield Footer()

    async def on_mount(self) -> None:
        index_name = self.query_one("#index_name", Input)
        search = self.query_one("#search", Input)
        async with get_client() as client:
            indexes = await client.get_indexes()

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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "load_more_button":
            self.limit += 20
            asyncio.create_task(self.lookup_word(self.query_one("#search", Input).value))

    async def lookup_word(self, search: str) -> None:
        index_name = self.query_one("#index_name", Input).value
        results = self.query_one("#results", Markdown)
        search = self.query_one("#search", Input).value
        if not index_name:
            await results.update("Error: No index provided")
            return

        async with get_client() as client:
            index = client.index(index_name)
            if search:
                try:
                    response = await index.search(search, limit=self.limit)
                    if response:
                        markdown = self.make_word_markdown(response)
                        await results.update(markdown)
                    else:
                        await results.update("")
                except Exception as e:
                    await self.query_one("#results", Markdown).update(f"Error: {e}")
                    return

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

        return ""
