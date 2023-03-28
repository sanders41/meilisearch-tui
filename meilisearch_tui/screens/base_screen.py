from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header


class BaseScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
