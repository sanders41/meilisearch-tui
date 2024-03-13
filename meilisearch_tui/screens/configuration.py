from __future__ import annotations

import asyncio

from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static, Switch

from meilisearch_tui.config import Theme, load_config
from meilisearch_tui.widgets.input import ErrorMessage, InputWithLabel
from meilisearch_tui.widgets.messages import SuccessMessage


class ConfigurationScreen(Screen):
    hybrid_search = False

    def compose(self) -> ComposeResult:
        with Container(id="body"):
            yield InputWithLabel(
                label="Server URL",
                input_id="server-url",
                input_placeholder="Can also be set with the MEILI_HTTP_ADDR enviornment vairable",
                error_id="server-url-error",
                error_message="A server URL is required",
            )
            yield InputWithLabel(
                label="Master Key",
                input_id="master-key",
                input_placeholder="Can also be set with the MEILI_MASTER_KEY enviornment vairable",
                error_id="master-key-error",
                password=True,
            )
            if self.hybrid_search:
                yield InputWithLabel(
                    label="Semantic Ratio",
                    input_id="semantic-ratio",
                    input_placeholder="Semantic ratio for hybrid search",
                    error_id="semantic-ratio-error",
                    error_message="Semantic ratio must be a float between 0.0 and 1.0",
                )
                yield InputWithLabel(
                    label="Embedder",
                    input_id="embedder",
                    input_placeholder="Embedder to use for hybrid search",
                    error_id="embedder-error",
                    error_message="An embedder is required",
                )
            yield Label("Dark Theme (restart required for change to take affect)")
            yield Switch(value=True, id="theme")
            with Center():
                yield Button(label="Save", id="save-setting-button")
            yield SuccessMessage(
                "Settings successfully saved",
                classes="message-centered",
                id="save-successful",
            )
            yield ErrorMessage("", classes="message-centered", id="save-error")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        is_error = False

        if button_id == "save-setting-button":
            server_url = self.query_one("#server-url", Input).value
            master_key = self.query_one("#master-key", Input).value
            config = load_config()

            if not config._meilisearch_url_env_var:
                config.meilisearch_url = server_url
            if not config._meilisearch_master_key_env_var:
                config.master_key = master_key

            theme_switch = self.query_one("#theme", Switch)
            if theme_switch.value:
                config.theme = Theme.DARK
            else:
                config.theme = Theme.LIGHT

            if self.hybrid_search:
                try:
                    semantic_ratio_str = self.query_one("#semantic-ratio", Input).value
                    if semantic_ratio_str == "":
                        raise ValueError("A semantic ratio is required for hybrid search")
                    semantic_ratio = float(semantic_ratio_str)
                    if semantic_ratio < 0.0 or semantic_ratio > 1.0:
                        raise ValueError("Semantic ratio must be between 0.0 and 1.0")
                    config.semantic_ratio = semantic_ratio
                except Exception:
                    self.query_one("#semantic-ratio-error", Static).visible = True
                    is_error = True

                embedder = self.query_one("#embedder", Input).value
                try:
                    if embedder == "":
                        raise ValueError("An embedder is required for hybrid search")
                    config.embedder = embedder
                except Exception:
                    self.query_one("#embedder-error", Static).visible = True
                    is_error = True

            if not config.meilisearch_url:
                self.query_one("#server-url-error", Static).visible = True
                is_error = True

            if not is_error:
                try:
                    config.save()
                    await self._success_message()
                except Exception as e:
                    await self._error_message(f"{e}")

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.query_one("#save-setting-button", Button).press()

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.query_one("#save-successful").visible = False
        server_url = self.query_one("#server-url", Input)
        server_url.focus()
        master_key = self.query_one("#master-key", Input)
        config = load_config()

        theme_switch = self.query_one("#theme", Switch)
        if config._meilisearch_url_env_var:
            server_url.value = "Set from MEILI_HTTP_ADDR environment variable"
            server_url.disabled = True
        elif config.meilisearch_url:
            server_url.value = config.meilisearch_url
            server_url.disabled = False

        if config._meilisearch_master_key_env_var:
            master_key.value = "Set from MEILI_MASTER_KEY enviornment variable"
            master_key.disabled = True
            master_key.password = False
        elif config.master_key:
            master_key.password = True
            master_key.value = config.master_key
            master_key.disabled = False

        if config.theme == Theme.DARK:
            theme_switch.value = True
        else:
            theme_switch.value = False

        if self.hybrid_search:
            semantic_ratio = self.query_one("#semantic-ratio", Input)
            if config.semantic_ratio:
                semantic_ratio.value = str(config.semantic_ratio)
            else:
                semantic_ratio.value = "0.5"

            embedder = self.query_one("#embedder", Input)
            if config.embedder:
                embedder.value = config.embedder
            else:
                embedder.value = "default"

    async def _success_message(self) -> None:
        success = self.query_one("#save-successful", Static)
        success.visible = True
        await asyncio.sleep(5)
        success.visible = False

    async def _error_message(self, message: str) -> None:
        error = self.query_one("#save-error", Static)
        error.renderable = message
        error.visible = True
        await asyncio.sleep(5)
        error.visible = False
