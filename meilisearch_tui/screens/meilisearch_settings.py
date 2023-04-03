from __future__ import annotations

from meilisearch_python_async.errors import MeilisearchCommunicationError
from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Static

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.messages import ErrorMessage


class MeilisearchSettings(Screen):
    def compose(self) -> ComposeResult:
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            yield Static("start", id="test")
        yield Footer()

    # def on_mount(self) -> None:
    #     print(f"{self.query_one('#index-sidebar').selected_index=}")
    #     self.query_one("#test").value = self.query_one("#index-sidebar").selected_index

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        body_container = self.query_one("#body", Container)
        error_message = self.query_one("#generic-error", ErrorMessage)
        body_container.visible = True
        error_message.display = False
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

        index_sidebar = self.query_one(IndexSidebar)
        if indexes:
            await index_sidebar.update([x.uid for x in indexes])
        else:
            await index_sidebar.update()
