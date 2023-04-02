from __future__ import annotations

import asyncio

from meilisearch_python_async.errors import (
    MeilisearchApiError,
    MeilisearchCommunicationError,
    MeilisearchError,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Static

from meilisearch_tui.client import get_client
from meilisearch_tui.config import load_config
from meilisearch_tui.utils import get_current_indexes_string
from meilisearch_tui.widgets.index import CurrentIndexes
from meilisearch_tui.widgets.input import InputWithLabel
from meilisearch_tui.widgets.messages import ErrorMessage, PageTitle, SuccessMessage


class AddIndexScreen(Screen):
    def compose(self) -> ComposeResult:
        with Container(id="body"):
            yield PageTitle("Add Indexes")
            yield InputWithLabel(
                label="Index Name",
                input_id="index_name",
                error_id="index_name_error",
                error_message="An index name is required",
            )
            yield InputWithLabel(
                label="Primary Key",
                input_id="primary_key",
                error_id="primary_key_error",
            )
            with Center():
                yield Button(label="Save", id="save_index_button")
            yield SuccessMessage(
                "Index successfully created",
                classes="message-centered",
                id="index_creation_successful",
            )
            yield ErrorMessage("", classes="message-centered", id="index_creation_error")
            yield CurrentIndexes()
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save_index_button":
            index_name = self.query_one("#index_name", Input).value
            primary_key = self.query_one("#primary_key", Input).value

            if not index_name:
                self.query_one("#index_name_error", Static).visible = True
            else:
                try:
                    async with get_client() as client:
                        await client.create_index(index_name, primary_key)

                    asyncio.create_task(self._success_message())
                    self.query_one("#index_name", Input).value = ""
                    self.query_one("#primary_key", Input).value = ""
                    self.query_one("#index_name", Input).focus()

                    indexes = await get_current_indexes_string()
                    self.query_one("#current_indexes", Static).update(indexes)
                except MeilisearchApiError as e:
                    asyncio.create_task(self._error_message(f"{e}"))
                except MeilisearchCommunicationError as e:
                    asyncio.create_task(self._error_message(f"{e}"))
                except MeilisearchError as e:
                    asyncio.create_task(self._error_message(f"{e}"))
                except Exception as e:
                    asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.query_one("#save_index_button", Button).press()

    def on_mount(self) -> None:
        self.query_one("#index_creation_successful", Static).visible = False
        self.query_one("#index_creation_error", Static).visible = False
        index_name = self.query_one("#index_name", Input)
        primary_key = self.query_one("#primary_key", Input)
        config = load_config()

        if config.meilisearch_url:
            self.query_one("#index_name", Input).focus()
        else:
            self.query_one("#index_name", Input).focus()
            index_name.placeholder = "Server URL not added to configuration"
            primary_key.placeholder = "Server URL not added to configuration"

    async def _success_message(self) -> None:
        success = self.query_one("#index_creation_successful", Static)
        success.visible = True
        await asyncio.sleep(5)
        success.visible = False

    async def _error_message(self, message: str) -> None:
        error = self.query_one("#index_creation_error", Static)
        error.renderable = message
        error.visible = True
        await asyncio.sleep(5)
        error.visible = False
