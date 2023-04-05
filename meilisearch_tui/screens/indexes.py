from __future__ import annotations

import asyncio
from functools import cached_property

from meilisearch_python_async.errors import (
    MeilisearchCommunicationError,
    MeilisearchError,
)
from meilisearch_python_async.models.settings import (
    MeilisearchSettings as MeilisearchSettingsResult,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container, Content
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Input,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.input import InputWithLabel
from meilisearch_tui.widgets.messages import ErrorMessage, SuccessMessage


class AddIndex(Widget):
    DEFAULT_CSS = """
    AddIndex {
        height: auto;
    }
    .hidden {
        visibility: hidden;
    }
    """

    class IndexAdded(Message):
        def __init__(self, added_index: str) -> None:
            self.added_index = added_index
            super().__init__()

    added_index = reactive("")

    def compose(self) -> ComposeResult:
        yield InputWithLabel(
            label="Index Name",
            input_id="index-name",
            input_placeholder="Required",
            error_id="index-name-error",
            error_message="Index name is required",
        )
        yield InputWithLabel(
            label="Primary Key",
            input_id="primary-key",
            error_id="primary-key-error",
        )
        yield SuccessMessage(
            "Data successfully sent for indexing",
            classes="message-centered, hidden",
            id="indexing-successful",
        )
        yield ErrorMessage("", classes="message-centered, hidden", id="indexing-error")
        with Center():
            yield Button("Save", id="save-button")

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_name(self) -> Input:
        return self.query_one("#index-name", Input)

    @cached_property
    def index_name_error(self) -> Static:
        return self.query_one("#index-name-error", Static)

    @cached_property
    def indexing_error(self) -> ErrorMessage:
        return self.query_one("#indexing-error", ErrorMessage)

    @cached_property
    def indexing_successful(self) -> SuccessMessage:
        return self.query_one("#indexing-successful", SuccessMessage)

    @cached_property
    def primary_key(self) -> Input:
        return self.query_one("#primary-key", Input)

    @cached_property
    def save_button(self) -> Button:
        return self.query_one("#save-button", Button)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.save_button.press()

    def on_mount(self) -> None:
        self.index_name.focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save-button":
            if not self.index_name.value:
                self.index_name_error.visible = True
                return None

            try:
                async with get_client() as client:
                    await client.create_index(self.index_name.value, self.primary_key.value)
                self.added_index = self.index_name.value
                asyncio.create_task(self._success_message())
            except MeilisearchError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except Exception as e:
                asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

        self.index_name.value = ""
        self.primary_key.value = ""
        self.index_name.focus()

    def watch_added_index(self) -> None:
        self.post_message(AddIndex.IndexAdded(self.added_index))

    async def _success_message(self) -> None:
        self.indexing_successful.visible = True
        await asyncio.sleep(5)
        self.indexing_successful.visible = False

    async def _error_message(self, message: str) -> None:
        self.indexing_error.renderable = message
        self.indexing_error.visible = True
        await asyncio.sleep(5)
        self.indexing_error.visible = False


class MeilisearchSettings(Widget):
    DEFAULT_CSS = """
    MeilisearchSettings {
        height: 90;
    }
    """
    selected_index: reactive[str | None] = reactive(None)

    @cached_property
    def body(self) -> Container:
        return self.query_one("#body", Container)

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_sidebar(self) -> IndexSidebar:
        return self.query_one(IndexSidebar)

    @cached_property
    def results(self) -> Markdown:
        return self.query_one("#results", Markdown)

    def compose(self) -> ComposeResult:
        with Content(id="results-container"):
            yield Markdown(id="results")

    async def watch_selected_index(self) -> None:
        asyncio.create_task(self.load_indexes())

    async def load_indexes(self) -> None:
        # save the selected index at the start to make sure it hasn't changed during the request
        current_index = self.selected_index

        if not self.selected_index:
            self.results.update("")
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            try:
                results = await index.get_settings()
            except Exception as e:
                if current_index == self.selected_index:
                    self.results.update(f"Error: {e}")
                return

        if current_index == self.selected_index:
            markdown = self.make_word_markdown(current_index, results)
            self.results.update(markdown)

    def make_word_markdown(self, index: str, results: MeilisearchSettingsResult) -> str:
        lines = []

        lines.append(f"# Settigns for {index} index")

        for k, v in results.dict().items():
            lines.append(f"## {k}\n{v}\n")

        return "\n".join(lines)


class IndexScreen(Screen):
    def compose(self) -> ComposeResult:
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            with TabbedContent(initial="index-settings"):
                with TabPane("Index Settings", id="index-settings"):
                    yield MeilisearchSettings()
                with TabPane("Add Index", id="add-index"):
                    yield AddIndex()
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield Footer()

    @cached_property
    def add_index(self) -> AddIndex:
        return self.query_one(AddIndex)

    @cached_property
    def body(self) -> Container:
        return self.query_one("#body", Container)

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_sidebar(self) -> IndexSidebar:
        return self.query_one(IndexSidebar)

    @cached_property
    def meilisearch_settings(self) -> MeilisearchSettings:
        return self.query_one(MeilisearchSettings)

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.body.visible = True
        self.generic_error.display = False
        await self.index_sidebar.update()
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError as e:
            self.body.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"  # type: ignore
            return
        except Exception as e:
            self.body.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}."  # type: ignore
            return

        if indexes:
            self.selected_index = self.index_sidebar.selected_index
            self.meilisearch_settings.selected_index = self.selected_index
        else:
            self.selected_index = None
            self.meilisearch_settings.selected_index = None

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        self.selected_index = self.index_sidebar.selected_index
        self.meilisearch_settings.selected_index = self.index_sidebar.selected_index or ""

    async def on_add_index_index_added(self) -> None:
        await self.index_sidebar.update()
