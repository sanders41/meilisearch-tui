from __future__ import annotations

from functools import cached_property

from meilisearch_python_sdk.errors import MeilisearchCommunicationError
from meilisearch_python_sdk.models.search import SearchResults
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
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
        with VerticalScroll(id="body"):
            yield Static("No index selected", id="index-name", classes="bottom-spacer")
            yield Input(placeholder="Search", classes="bottom-spacer", id="search")
            with Center():
                yield Button(label="Clear Search Box", classes="bottom-spacer", id="clear-search")
            with VerticalScroll(id="results-container"):
                yield Markdown(id="results")
            with Center():
                yield Button(label="Load More", classes="bottom-spacer", id="load-more-button")
        yield Footer()

    @cached_property
    def body_container(self) -> VerticalScroll:
        return self.query_one("#body", VerticalScroll)

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_sidebar(self) -> IndexSidebar:
        return self.query_one(IndexSidebar)

    @cached_property
    def index_name(self) -> Static:
        return self.query_one("#index-name", Static)

    @cached_property
    def search_input(self) -> Input:
        return self.query_one("#search", Input)

    @cached_property
    def clear_search(self) -> Button:
        return self.query_one("#clear-search", Button)

    @cached_property
    def results_container(self) -> VerticalScroll:
        return self.query_one("#results-container", VerticalScroll)

    @cached_property
    def results(self) -> Markdown:
        return self.query_one("#results", Markdown)

    @cached_property
    def load_more_button(self) -> Button:
        return self.query_one("#load-more-button", Button)

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.body_container.visible = True
        self.generic_error.display = False
        await self.index_sidebar.update()
        self.search_input.value = ""
        self.results.update("")
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError as e:
            self.body_container.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"  # type: ignore
            return
        except Exception as e:
            self.body_container.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}."  # type: ignore
            return

        if indexes:
            self.index_name.update(f"Searching index: {indexes[0].uid}")
            self.selected_index = self.index_sidebar.selected_index
        else:
            self.selected_index = None
            self.index_name.update("No index selected")

        self.search_input.focus()
        self.load_more_button.visible = False

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        self.selected_index = self.index_sidebar.selected_index
        self.index_name.update(f"Searching index: {self.selected_index}")
        self.search_input.value = ""
        self.results.update("")

    async def on_input_changed(self, message: Input.Changed) -> None:
        self.limit = 20
        if message.value:
            await self.search(message.value)
        else:
            self.results.update("")
            self.load_more_button.visible = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "load-more-button":
            self.limit += 20
            await self.search(self.search_input.value)

        if button_id == "clear-search":
            self.search_input.value = ""
            self.search_input.focus()

    async def search(self, search: str) -> None:
        if not self.selected_index and search == self.search_input.value:
            self.results.update("Error: No index provided")
            return

        if not self.selected_index:
            self.results.update("No index selected")
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            try:
                results = await index.search(
                    self.search_input.value,
                    limit=self.limit,
                    attributes_to_highlight=["*"],
                    highlight_pre_tag="***",
                    highlight_post_tag="***",
                )

            except Exception as e:
                if search == self.search_input.value:
                    self.results.update(f"Error: {e}")
                return

        # Make sure a new search hasn't started. This prevents race conditions with displaying
        # the search results by only updating the display if the search is still relavent.
        if search == self.search_input.value:
            markdown = self.make_word_markdown(results)
            self.results.update(markdown)

    def make_word_markdown(self, results: SearchResults) -> str:
        lines = []

        if results.estimated_total_hits and results.estimated_total_hits > len(results.hits):
            self.load_more_button.visible = True
        else:
            self.load_more_button.visible = False

        lines.append(
            f"## Hits: ~{results.estimated_total_hits} | Search time: {results.processing_time_ms} ms"
        )

        if results.hits:
            for hit in results.hits:
                if hit.get("_formatted"):
                    for k, v in hit["_formatted"].items():
                        lines.append(f"{k}: {v}\n")
                else:
                    for k, v in hit.items():
                        lines.append(f"{k}: {v}\n")
                lines.append("-------------------------------")
            return "\n".join(lines)

        return "No results found"
