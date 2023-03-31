from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from meilisearch_tui.widgets.sidebar import Sidebar


class Welcome(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")
        yield Static("Welcome")
