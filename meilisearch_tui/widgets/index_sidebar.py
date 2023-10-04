from __future__ import annotations

from meilisearch_python_sdk.errors import MeilisearchCommunicationError
from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView

from meilisearch_tui.client import get_client


class IndexSidebar(ListView):
    def __init__(self, *, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.indexes: list[str] = []

    def compose(self) -> ComposeResult:
        yield ListItem(Label("No Index retrieval"))

    @property
    def selected_index(self) -> str | None:
        if self.index is not None and 0 <= self.index < len(self.indexes):
            return self.indexes[self.index]

        return None

    async def update(self) -> None:
        await self.clear()
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError:
            await self.append(ListItem(Label("Error connecting to server")))
            self.indexes = []
            return
        except Exception:
            await self.append(ListItem(Label("Error retrieving indexes")))
            self.indexes = []
            return

        if not indexes:
            await self.append(ListItem(Label("No indexes")))
            self.indexes = []
            return

        for index in indexes:
            self.indexes = [x.uid for x in indexes]
            await self.append(ListItem(Label(index.uid)))
        self.index = 0
