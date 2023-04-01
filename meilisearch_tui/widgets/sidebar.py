from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Content
from textual.widget import Widget
from textual.widgets import Static


class Sidebar(Widget):
    DEFAULT_CSS = """
    Sidebar {
        background: $primary;
        color: $secondary;
        overflow: auto;
        width: 20;
        height: 100%;
        dock: left;
        margin-right: 5;
        padding: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Content(id="sidebar"):
            yield Static("Configuration")
            yield Static("Search")
            yield Static("Index")
            yield Static("Load Data")
