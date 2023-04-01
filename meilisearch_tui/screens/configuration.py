from __future__ import annotations

import asyncio

from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static, Switch

from meilisearch_tui.config import Theme, config
from meilisearch_tui.widgets.input import ErrorMessage, InputWithLabel
from meilisearch_tui.widgets.messages import SuccessMessage


class ConfigurationScreen(Screen):
    def compose(self) -> ComposeResult:
        with Container(id="body"):
            yield InputWithLabel(
                label="Server URL",
                input_id="server_url",
                error_id="server_url_error",
                error_message="A server URL is required",
            )
            yield InputWithLabel(
                label="Master Key",
                input_id="master_key",
                input_placeholder="Can also be set with the MEILI_MASTER_KEY enviornment vairable",
                error_id="master_key_error",
                password=True,
            )
            yield Label("Dark Theme (restart required for change to take affect)")
            yield Switch(value=True, id="theme")
            with Center():
                yield Button(label="Save", id="save_setting_button")
            yield SuccessMessage(
                "Settings successfully saved",
                classes="message-centered",
                id="save_successful",
            )
            yield ErrorMessage("", classes="message-centered", id="save_error")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save_setting_button":
            server_url = self.query_one("#server_url", Input).value
            master_key = self.query_one("#master_key", Input).value

            config.meilisearch_url = server_url
            config.master_key = master_key

            theme_switch = self.query_one("#theme", Switch)
            if theme_switch.value:
                config.theme = Theme.DARK
            else:
                config.theme = Theme.LIGHT

            if not config.meilisearch_url:
                self.query_one("#server_url_error", Static).visible = True
            else:
                try:
                    config.save()
                    asyncio.create_task(self._success_message())
                except Exception as e:
                    asyncio.create_task(self._error_message(f"{e}"))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.query_one("#save_setting_button", Button).press()

    def on_mount(self) -> None:
        self.query_one("#save_successful").visible = False
        self.query_one("#server_url", Input).focus()

        theme_switch = self.query_one("#theme", Switch)
        if config.meilisearch_url:
            self.query_one("#server_url", Input).value = config.meilisearch_url
        if config.master_key:
            self.query_one("#master_key", Input).value = config.master_key
        if config.theme == Theme.DARK:
            theme_switch.value = True
        else:
            theme_switch.value = False

    async def _success_message(self) -> None:
        success = self.query_one("#save_successful", Static)
        success.visible = True
        await asyncio.sleep(5)
        success.visible = False

    async def _error_message(self, message: str) -> None:
        error = self.query_one("#save_error", Static)
        error.renderable = message
        error.visible = True
        await asyncio.sleep(5)
        error.visible = False
