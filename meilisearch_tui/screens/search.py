from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer


class SearchScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Footer()
