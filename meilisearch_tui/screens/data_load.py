from __future__ import annotations

import asyncio
from functools import cached_property
from pathlib import Path

from meilisearch_python_async.errors import (
    MeilisearchApiError,
    MeilisearchCommunicationError,
    MeilisearchError,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Input, Static

from meilisearch_tui.client import get_client
from meilisearch_tui.widgets.index import CurrentIndexes
from meilisearch_tui.widgets.input import InputWithLabel
from meilisearch_tui.widgets.messages import ErrorMessage, SuccessMessage


class DataLoadScreen(Screen):
    def compose(self) -> ComposeResult:
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        with Container(id="body"):
            yield DirectoryTree(Path.home(), id="tree-view")
            yield InputWithLabel(
                label="Index",
                input_id="index-name",
                error_id="index-error",
                error_message="An index is require",
            )
            yield InputWithLabel(
                label="File Path",
                input_id="data-file",
                error_id="data-file-error",
                error_message="A Path to a json, jsonl, or csv file is required",
            )
            with Center():
                yield Button(label="Index File", id="index-button")
            yield SuccessMessage(
                "Data successfully sent for indexing",
                classes="message-centered",
                id="indexing-successful",
            )
            yield ErrorMessage("", classes="message-centered", id="indexing-error")
            yield CurrentIndexes()
        yield Footer()

    @cached_property
    def body(self) -> Container:
        return self.query_one("#body", Container)

    @cached_property
    def current_indexes(self) -> CurrentIndexes:
        return self.query_one(CurrentIndexes)

    @cached_property
    def data_file(self) -> Input:
        return self.query_one("#data-file", Input)

    @cached_property
    def data_file_error(self) -> Static:
        return self.query_one("#data-file-error", Static)

    @cached_property
    def directory_tree(self) -> DirectoryTree:
        return self.query_one("#tree-view", DirectoryTree)

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_button(self) -> Button:
        return self.query_one("#index-button", Button)

    @cached_property
    def index_error(self) -> Static:
        return self.query_one("#index-error", Static)

    @cached_property
    def index_name(self) -> Input:
        return self.query_one("#index-name", Input)

    @cached_property
    def indexing_successful(self) -> Static:
        return self.query_one("#indexing-successful", Static)

    @cached_property
    def indexing_error(self) -> Static:
        return self.query_one("#indexing-error", Static)

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.body.visible = True
        self.generic_error.display = False
        try:
            async with get_client() as client:
                indexes = await client.get_indexes()
        except MeilisearchCommunicationError as e:
            self.body.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"  # type: ignore
            return
        except Exception as e:
            self.body.visible = False
            self.generic_error.display = True
            self.generic_error.renderable = f"An error occured: {e}."  # type: ignore
            return

        if indexes:
            self.index_name.value = indexes[0].uid
            self.directory_tree.focus()
        else:
            self.index_name.focus()

        await self.current_indexes.update()
        self.indexing_successful.visible = False
        self.indexing_error.visible = False

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        try:
            self.data_file.value = event.path
        except Exception:
            raise

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        error = False

        if button_id == "index-button":
            if not self.data_file.value or Path(self.data_file.value).suffix not in (
                ".csv",
                ".json",
                ".jsonl",
            ):
                self.data_file_error.visible = True
                error = True
            if not self.index_name.value:
                self.index_error.visible = True
                error = True

            if error:
                return None

            data_file_path = Path(self.data_file.value)
            try:
                async with get_client() as client:
                    index = client.index(self.index_name.value)
                    if data_file_path.suffix == ".json":
                        await index.add_documents_from_file_in_batches(data_file_path)
                    else:
                        await index.add_documents_from_raw_file(data_file_path)
                asyncio.create_task(self._success_message())
            except MeilisearchApiError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except MeilisearchCommunicationError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except MeilisearchError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except Exception as e:
                asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

        await self.current_indexes.update()

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.index_button.press()

    async def _success_message(self) -> None:
        self.indexing_successful.visible = True
        await asyncio.sleep(5)
        self.indexing_successful.visible = False

    async def _error_message(self, message: str) -> None:
        self.indexing_error.renderable = message
        self.indexing_error.visible = True
        await asyncio.sleep(5)
        self.indexing_error.visible = False
