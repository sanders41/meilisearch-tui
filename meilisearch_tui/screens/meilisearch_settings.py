from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Static

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
            yield Static("start", id="test")
        yield Footer()

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        body_container = self.query_one("#body", Container)
        error_message = self.query_one("#generic-error", ErrorMessage)
        body_container.visible = True
        error_message.display = False
        index_sidebar = self.query_one(IndexSidebar)
        await index_sidebar.update()
        self.selected_index = index_sidebar.selected_index
        if self.selected_index:
            self.query_one("#test", Static).update(self.selected_index)

    def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        index_sidebar = self.query_one(IndexSidebar)
        self.selected_index = index_sidebar.selected_index
        if self.selected_index:
            self.query_one("#test", Static).update(self.selected_index)
