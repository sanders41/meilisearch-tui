from __future__ import annotations

import asyncio
from functools import cached_property

from meilisearch_python_async.errors import MeilisearchCommunicationError
from meilisearch_python_async.models.settings import (
    MeilisearchSettings as MeilisearchSettingsResult,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Content
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Markdown, Static, TabbedContent, TabPane

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.messages import ErrorMessage


class AddIndex(Widget):
    DEFAULT_CSS = """
    AddIndex {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Add index")


# TABS = ("Add Index", "Update Index", "Delete Index", "Index Settings")
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

    # @cached_property
    # def tabs(self) -> Tabs:
    #    return self.query_one(Tabs)

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

    #         self.body.visible = True
    #         self.generic_error.display = False
    #         await self.index_sidebar.update()
    #         try:
    #             async with get_client() as client:
    #                 indexes = await client.get_indexes()
    #         except MeilisearchCommunicationError as e:
    #             self.body.visible = False
    #             self.generic_error.display = True
    #             self.generic_error.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"  # type: ignore
    #             return
    #         except Exception as e:
    #             self.body.visible = False
    #             self.generic_error.display = True
    #             self.generic_error.renderable = f"An error occured: {e}."  # type: ignore
    #             return
    #
    #         if indexes:
    #             self.index_name.update(f"Searching index: {indexes[0].uid}")
    #             self.selected_index = self.index_sidebar.selected_index
    #         else:
    #             self.selected_index = None
    #             self.index_name.update("No index selected")
    #
    #         self.search_input.focus()
    #         self.load_more_button.visible = False

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        self.selected_index = self.index_sidebar.selected_index
        self.meilisearch_settings.selected_index = self.index_sidebar.selected_index or ""
