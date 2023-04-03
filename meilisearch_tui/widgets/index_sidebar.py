from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView


class IndexSidebar(ListView):
    def __init__(self, classes: str) -> None:
        super().__init__(classes=classes)

    def compose(self) -> ComposeResult:
        yield ListItem(Label("No indexes"))

    async def update(self, index_choices: list[str] | None = None) -> None:
        await self.clear()
        if not index_choices:
            await self.append(ListItem(Label("No indexes")))
            return None

        for index in index_choices:
            await self.append(ListItem(Label(index)))
