from __future__ import annotations

from functools import cached_property

from meilisearch_python_async.errors import MeilisearchCommunicationError
from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Tabs

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.messages import ErrorMessage

TABS = ("Add Index", "Update Index", "Delete Index", "Index Settings")


class IndexScreen(Screen):
    DEFAULT_CSS = """
    Tabs {
        dock: top;
    }
    """

    def compose(self) -> ComposeResult:
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            yield Tabs(*TABS)
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
    def tabs(self) -> Tabs:
        return self.query_one(Tabs)

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
            self.index_name.update(f"Searching index: {indexes[0].uid}")
            self.selected_index = self.index_sidebar.selected_index
        else:
            self.selected_index = None
            self.index_name.update("No index selected")

        self.search_input.focus()
        self.load_more_button.visible = False
