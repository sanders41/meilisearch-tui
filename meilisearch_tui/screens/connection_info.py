from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label


class ConnectionInfo(Screen):
    def compose(self) -> ComposeResult:
        yield Label("Server URL")
        yield Input(placeholder="Server URL", id="server_url")
        yield Label("Master Key")
        yield Input(placeholder="Master Key", id="master_key")
        yield Button(label="Save", id="save_setting_button")
