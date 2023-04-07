from __future__ import annotations

import asyncio
import json
from functools import cached_property
from pathlib import Path

from meilisearch_python_async.errors import (
    MeilisearchCommunicationError,
    MeilisearchError,
)
from meilisearch_python_async.models.settings import (
    MeilisearchSettings as MeilisearchSettingsInfo,
)
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Container, Content, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Input,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)

from meilisearch_tui.client import get_client
from meilisearch_tui.utils import string_to_list
from meilisearch_tui.widgets.index_sidebar import IndexSidebar
from meilisearch_tui.widgets.input import InputWithLabel
from meilisearch_tui.widgets.messages import ErrorMessage, SuccessMessage


class AddIndex(Widget):
    DEFAULT_CSS = """
    AddIndex {
        height: auto;
    }
    .hidden {
        visibility: hidden;
    }
    """

    class IndexAdded(Message):
        def __init__(self, added_index: str) -> None:
            self.added_index = added_index
            super().__init__()

    added_index = reactive("")

    def compose(self) -> ComposeResult:
        yield InputWithLabel(
            label="Index Name",
            input_id="index-name",
            input_placeholder="Required",
            error_id="index-name-error",
            error_message="Index name is required",
        )
        yield InputWithLabel(
            label="Primary Key",
            input_id="primary-key",
            error_id="primary-key-error",
        )
        yield SuccessMessage(
            "Index successfully created",
            classes="message-centered, hidden",
            id="indexing-successful",
        )
        yield ErrorMessage("", classes="message-centered, hidden", id="indexing-error")
        with Center():
            yield Button("Save", id="save-button")

    @cached_property
    def index_name(self) -> Input:
        return self.query_one("#index-name", Input)

    @cached_property
    def index_name_error(self) -> Static:
        return self.query_one("#index-name-error", Static)

    @cached_property
    def indexing_error(self) -> ErrorMessage:
        return self.query_one("#indexing-error", ErrorMessage)

    @cached_property
    def indexing_successful(self) -> SuccessMessage:
        return self.query_one("#indexing-successful", SuccessMessage)

    @cached_property
    def primary_key(self) -> Input:
        return self.query_one("#primary-key", Input)

    @cached_property
    def save_button(self) -> Button:
        return self.query_one("#save-button", Button)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.save_button.press()

    def on_mount(self) -> None:
        self.index_name.focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save-button":
            if not self.index_name.value:
                self.index_name_error.visible = True
                return None

            try:
                async with get_client() as client:
                    await client.create_index(self.index_name.value, self.primary_key.value)
                self.added_index = self.index_name.value
                asyncio.create_task(self._success_message())
            except MeilisearchError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except Exception as e:
                asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

        self.index_name.value = ""
        self.primary_key.value = ""
        self.index_name.focus()

    def watch_added_index(self) -> None:
        self.post_message(AddIndex.IndexAdded(self.added_index))

    async def _success_message(self) -> None:
        self.indexing_successful.visible = True
        await asyncio.sleep(5)
        self.indexing_successful.visible = False

    async def _error_message(self, message: str) -> None:
        self.indexing_error.renderable = message
        self.indexing_error.visible = True
        await asyncio.sleep(5)
        self.indexing_error.visible = False


class DeleteIndex(Widget):
    DEFAULT_CSS = """
    DeleteIndex {
        height: auto;
    }
    """

    selected_index: reactive[str | None] = reactive(None)

    class IndexDeleted(Message):
        def __init__(self) -> None:
            self.selected_index = None
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(
            "No index selected", classes="message-centered bottom-spacer", id="index-delete-name"
        )
        yield SuccessMessage(
            "Index deleted",
            classes="message-centered, hidden",
            id="index-delete-successful",
        )
        yield ErrorMessage("", classes="message-centered, hidden", id="index-delete-error")
        with Center():
            yield Button("Delete Index", id="index-delete-button")

    @cached_property
    def index_name(self) -> Static:
        return self.query_one("#index-delete-name", Static)

    @cached_property
    def delete_button(self) -> Button:
        return self.query_one("#indexdelete-button", Button)

    @cached_property
    def indexing_error(self) -> ErrorMessage:
        return self.query_one("#index-delete-error", ErrorMessage)

    @cached_property
    def indexing_successful(self) -> SuccessMessage:
        return self.query_one("#index-delete-successful", SuccessMessage)

    async def watch_selected_index(self) -> None:
        if self.selected_index:
            self.index_name.update(f"Index to delete: {self.selected_index}")
        else:
            self.index_name.update("No index selected")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "delete-button":
            if not self.selected_index:
                self.selected_index = "No index selected"
                return None

            try:
                async with get_client() as client:
                    index = client.index(self.selected_index)
                    await index.delete()
                asyncio.create_task(self._success_message())
            except MeilisearchError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except Exception as e:
                asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

        self.selected_index = None
        self.post_message(DeleteIndex.IndexDeleted())

    async def _success_message(self) -> None:
        self.indexing_successful.visible = True
        await asyncio.sleep(5)
        self.indexing_successful.visible = False

    async def _error_message(self, message: str) -> None:
        self.indexing_error.renderable = message
        self.indexing_error.visible = True
        await asyncio.sleep(5)
        self.indexing_error.visible = False


class DataLoad(Widget):
    DEFAULT_CSS = """
    DataLoad {
        height: 50;
    }
    """

    selected_index: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield DirectoryTree(Path.home(), id="tree-view")
        yield Static("No index selected", classes="bottom-spacer", id="data-load-index-name")
        yield InputWithLabel(
            label="File Path",
            input_id="data-file",
            error_id="data-file-error",
            error_message="A Path to a json, jsonl, or csv file is required",
        )
        with Center():
            yield Button(label="Load Data", id="load-data-button")
        yield SuccessMessage(
            "Data successfully sent for indexing",
            classes="message-centered",
            id="load-data-successful",
        )
        yield ErrorMessage("", classes="message-centered", id="load-data-error")

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
    def load_data_button(self) -> Button:
        return self.query_one("#load-data-button", Button)

    @cached_property
    def data_load_error(self) -> Static:
        return self.query_one("#load-data-error", Static)

    @cached_property
    def index_name(self) -> Static:
        return self.query_one("#data-load-index-name", Static)

    @cached_property
    def data_load_successful(self) -> Static:
        return self.query_one("#load-data-successful", Static)

    def on_mount(self) -> None:
        self.data_load_successful.visible = False
        self.data_load_error.visible = False
        self.data_file.focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        try:
            self.data_file.value = event.path
        except Exception:
            raise

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "load-data-button":
            selected_index = self.selected_index
            if not self.data_file.value or Path(self.data_file.value).suffix not in (
                ".csv",
                ".json",
                ".jsonl",
            ):
                self.data_file_error.visible = True
                return None
            if not selected_index:
                return None

            data_file_path = Path(self.data_file.value)
            try:
                async with get_client() as client:
                    index = client.index(selected_index)
                    if data_file_path.suffix == ".json":
                        await index.add_documents_from_file_in_batches(data_file_path)
                    else:
                        await index.add_documents_from_raw_file(data_file_path)
                asyncio.create_task(self._success_message())
            except MeilisearchError as e:
                asyncio.create_task(self._error_message(f"{e}"))
            except Exception as e:
                asyncio.create_task(self._error_message(f"An unknown error occured error: {e}"))

        self.data_file.value = ""

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.load_data_button.press()

    async def watch_selected_index(self) -> None:
        if self.selected_index:
            self.index_name.update(f"Selected Index: {self.selected_index}")
        else:
            self.index_name.update("No index selected")

    async def _success_message(self) -> None:
        self.data_load_successful.visible = True
        await asyncio.sleep(5)
        self.data_load_successful.visible = False

    async def _error_message(self, message: str) -> None:
        self.data_load_error.renderable = message
        self.data_load_error.visible = True
        await asyncio.sleep(5)
        self.data_load_error.visible = False


class EditMeilisearchSettings(Widget):
    DEFAULT_CSS = """
    EditMeilisearchSettings {
        height: auto;
    }
    ErrorMessage {
        padding-top: 1;
        text-align: center;
    }
    Horizontal {
        height: auto;
        width: auto;
    }
    Button {
        margin: 0 1;
    }
    """

    settings_saved = reactive(False, layout=True)

    class SettingsSaved(Message):
        def __init__(self, settings_saved: bool) -> None:
            self.settings_saved = settings_saved
            super().__init__()

    selected_index: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield InputWithLabel(
            label="Synonyms",
            input_id="synonyms-input",
            input_placeholder='Example: {"car": ["vehicle", "automobile"]}',
            error_id="synonyms-input-error",
        )
        yield InputWithLabel(
            label="Stop Words",
            input_id="stop-words-input",
            input_placeholder='Example: ["a", "an", "the"]',
            error_id="stop-words-input-error",
        )
        yield InputWithLabel(
            label="Ranking Rules",
            input_id="ranking-rules-input",
            input_placeholder='Example: ["words", "typo", "proximity", "attribute", "sort", "exactness"]',
            error_id="stop-words-input-error",
        )
        yield InputWithLabel(
            label="Filterable Attributes",
            input_id="filterable-attributes-input",
            input_placeholder='Example: ["genres", "director", "release_date.year"]',
            error_id="filterable-attributes-input-error",
        )
        yield InputWithLabel(
            label="Distinct Attribute",
            input_id="distinct-attribute-input",
            input_placeholder="Example: movie_id",
            error_id="distinct-attribute-input-error",
        )
        yield InputWithLabel(
            label="Searchable Attributes",
            input_id="searchable-attributes-input",
            input_placeholder='Example: ["title", "overview"]',
            error_id="searchable-attributes-input-error",
        )
        yield InputWithLabel(
            label="Displayed Attributes",
            input_id="displayed-attributes-input",
            input_placeholder='Example: ["title", "overview"]',
            error_id="displayed-attributes-input-error",
        )
        yield InputWithLabel(
            label="Sortable Attributes",
            input_id="sortable-attributes-input",
            input_placeholder='Example: ["title", "release_date.year"]',
            error_id="sortable-attributes-input-error",
        )
        yield InputWithLabel(
            label="Typo Tolerance",
            input_id="typo-tolerance-input",
            input_placeholder='Example: {"enabled": true, "min_word_size_for_typos": {"one_typo": 5, "two_typos": 9}, "disable_on_words": [], "disable_on_attributes": []}',
            error_id="typo-tolerance-input-error",
        )
        yield InputWithLabel(
            label="Faceting",
            input_id="faceting-input",
            input_placeholder='Example: {"max_values_per_facet": 100}',
            error_id="faceting-input-error",
        )
        yield InputWithLabel(
            label="Patination",
            input_id="pagination-input",
            input_placeholder='Example: {"max_total_hits": 1000}',
            error_id="pagination-input-error",
        )
        with Center():
            with Horizontal():
                yield Button("Save", id="save-settings-button")
                yield Button("Cancel", id="cancel-button")
        yield ErrorMessage(id="edit-settings-error")

    @cached_property
    def synonyms_input(self) -> Input:
        return self.query_one("#synonyms-input", Input)

    @cached_property
    def stop_words_input(self) -> Input:
        return self.query_one("#stop-words-input", Input)

    @cached_property
    def ranking_rules_input(self) -> Input:
        return self.query_one("#ranking-rules-input", Input)

    @cached_property
    def filterable_attributes_input(self) -> Input:
        return self.query_one("#filterable-attributes-input", Input)

    @cached_property
    def distinct_attribute_input(self) -> Input:
        return self.query_one("#distinct-attribute-input", Input)

    @cached_property
    def searchable_attributes_input(self) -> Input:
        return self.query_one("#searchable-attributes-input", Input)

    @cached_property
    def displayed_attributes_input(self) -> Input:
        return self.query_one("#displayed-attributes-input", Input)

    @cached_property
    def sortable_attributes_input(self) -> Input:
        return self.query_one("#sortable-attributes-input", Input)

    @cached_property
    def typo_tolerance_input(self) -> Input:
        return self.query_one("#typo-tolerance-input", Input)

    @cached_property
    def faceting_input(self) -> Input:
        return self.query_one("#faceting-input", Input)

    @cached_property
    def pagination_input(self) -> Input:
        return self.query_one("#pagination-input", Input)

    @cached_property
    def save_button(self) -> Button:
        return self.query_one("#save-settings-button", Button)

    @cached_property
    def cancel_button(self) -> Button:
        return self.query_one("#cancel-button", Button)

    @cached_property
    def edit_settings_error(self) -> ErrorMessage:
        return self.query_one("#edit-settings-error", ErrorMessage)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save-settings-button" and self.selected_index:
            try:
                synonyms = (
                    json.loads(self.synonyms_input.value) if self.synonyms_input.value else None
                )
                stop_words = string_to_list(self.stop_words_input.value)
                ranking_rules = string_to_list(self.ranking_rules_input.value)
                filterable_attributes = string_to_list(self.filterable_attributes_input.value)
                distinct_attribute = self.distinct_attribute_input.value or None
                searchable_attributes = string_to_list(self.sortable_attributes_input.value)
                typo_tolerance = (
                    json.loads(self.typo_tolerance_input.value)
                    if self.typo_tolerance_input.value
                    else None
                )
                faceting = (
                    json.loads(self.faceting_input.value) if self.faceting_input.value else None
                )
                pagination = (
                    json.loads(self.pagination_input.value) if self.pagination_input.value else None
                )

                settings = MeilisearchSettingsInfo(
                    synonyms=synonyms,
                    stop_words=stop_words,
                    ranking_rules=ranking_rules,
                    filterable_attributes=filterable_attributes,
                    distinct_attribute=distinct_attribute,
                    searchable_attributes=searchable_attributes,
                    typo_tolerance=typo_tolerance,
                    faceting=faceting,
                    pagination=pagination,
                )

                async with get_client() as client:
                    index = client.index(self.selected_index)
                    await index.update_settings(settings)
            except Exception as e:
                asyncio.create_task(self._error_message(f"An error accurred saving settings: {e}"))
                return

        self.synonyms_input.value = ""
        self.stop_words_input.value = ""
        self.ranking_rules_input.value = ""
        self.filterable_attributes_input.value = ""
        self.distinct_attribute_input.value = ""
        self.searchable_attributes_input.value = ""
        self.typo_tolerance_input.value = ""
        self.faceting_input.value = ""
        self.pagination_input.value = ""

        self.settings_saved = True

    async def watch_selected_index(self) -> None:
        if not self.selected_index:
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            results = await index.get_settings()

        self.synonyms_input.value = json.dumps(results.synonyms) if results.synonyms else "{}"
        self.stop_words_input.value = str(results.stop_words)
        self.ranking_rules_input.value = str(results.ranking_rules)
        self.filterable_attributes_input.value = str(results.filterable_attributes)
        self.distinct_attribute_input.value = results.distinct_attribute or ""
        self.searchable_attributes_input.value = str(results.searchable_attributes)
        self.displayed_attributes_input.value = str(results.displayed_attributes)
        self.sortable_attributes_input.value = str(results.sortable_attributes)
        self.typo_tolerance_input.value = (
            results.typo_tolerance.json() if results.typo_tolerance else "{}"
        )
        self.faceting_input.value = results.faceting.json() if results.faceting else "{}"
        self.pagination_input.value = results.pagination.json() if results.pagination else "{}"
        self.synonyms_input.focus()

    def watch_settings_saved(self) -> None:
        if self.settings_saved:
            self.post_message(EditMeilisearchSettings.SettingsSaved(True))

        self.settings_saved = False

    async def _error_message(self, message: str) -> None:
        self.edit_settings_error.renderable = message
        self.edit_settings_error.display = True
        await asyncio.sleep(5)
        self.edit_settings_error.display = False


class MeilisearchSettings(Widget):
    DEFAULT_CSS = """
    MeilisearchSettings {
        height: 90;
    }
    """

    selected_index: reactive[str | None] = reactive(None, layout=True)
    edit_view = reactive(False, layout=True)

    def compose(self) -> ComposeResult:
        with Content(id="results-container"):
            yield Markdown(id="results")
            with Center():
                yield Button("Edit Settings", id="edit-settings-button")
        with Content(id="edit-settings"):
            yield EditMeilisearchSettings()

    @cached_property
    def results(self) -> Markdown:
        return self.query_one("#results", Markdown)

    @cached_property
    def results_container(self) -> Content:
        return self.query_one("#results-container", Content)

    @cached_property
    def edit_settings_button(self) -> Button:
        return self.query_one("#edit-settings-button", Button)

    @cached_property
    def edit_settings_container(self) -> Content:
        return self.query_one("#edit-settings", Content)

    @cached_property
    def edit_meilisearch_settings(self) -> EditMeilisearchSettings:
        return self.query_one(EditMeilisearchSettings)

    async def watch_selected_index(self) -> None:
        asyncio.create_task(self.load_settings())
        self.edit_meilisearch_settings.selected_index = self.selected_index

    def watch_edit_view(self) -> None:
        if self.edit_view:
            self.results_container.display = False
            self.edit_settings_container.display = True
        else:
            self.results_container.display = True
            self.edit_settings_container.display = False

    async def on_edit_meilisearch_settings_settings_saved(
        self, event: EditMeilisearchSettings.SettingsSaved
    ) -> None:
        if event.settings_saved:
            self.edit_view = False
            asyncio.create_task(self.load_settings())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "edit-settings-button":
            self.edit_view = True

    async def load_settings(self) -> None:
        # save the selected index at the start to make sure it hasn't changed during the request
        current_index = self.selected_index

        if not self.selected_index:
            self.results.update("")
            return

        async with get_client() as client:
            index = client.index(self.selected_index)
            try:
                results = await index.get_settings()
            except Exception as e:
                if current_index == self.selected_index:
                    self.results.update(f"Error: {e}")
                return

        if current_index == self.selected_index:
            if results:
                markdown = self.make_word_markdown(current_index, results)
                self.results.update(markdown)
            else:
                self.results.update("No indexes")
                self.edit_settings_button.display = False

    def make_word_markdown(self, index: str, results: MeilisearchSettingsInfo) -> str:
        lines = []

        lines.append(f"# Settigns for {index} index")

        for k, v in results.dict().items():
            lines.append(f"## {k.replace('_', ' ').title()}\n{v}\n")

        return "\n".join(lines)


class IndexScreen(Screen):
    def compose(self) -> ComposeResult:
        yield IndexSidebar(classes="sidebar")
        with Container(id="body"):
            with TabbedContent(initial="index-settings"):
                with TabPane("Index Settings", id="index-settings"):
                    yield MeilisearchSettings()
                with TabPane("Add Index", id="add-index"):
                    yield AddIndex()
                with TabPane("Delete Index", id="delete-index"):
                    yield DeleteIndex()
                with TabPane("Load Data", id="load-data"):
                    yield DataLoad()
        yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield Footer()

    @cached_property
    def add_index(self) -> AddIndex:
        return self.query_one(AddIndex)

    @cached_property
    def body(self) -> Container:
        return self.query_one("#body", Container)

    @cached_property
    def data_load(self) -> DataLoad:
        return self.query_one(DataLoad)

    @cached_property
    def delete_index(self) -> DeleteIndex:
        return self.query_one(DeleteIndex)

    @cached_property
    def generic_error(self) -> ErrorMessage:
        return self.query_one("#generic-error", ErrorMessage)

    @cached_property
    def index_sidebar(self) -> IndexSidebar:
        return self.query_one(IndexSidebar)

    @cached_property
    def meilisearch_settings(self) -> MeilisearchSettings:
        return self.query_one(MeilisearchSettings)

    @cached_property
    def tabbed_content(self) -> TabbedContent:
        return self.query_one(TabbedContent)

    async def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.body.visible = True
        self.generic_error.display = False
        await self.index_sidebar.update()
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
            self.selected_index = self.index_sidebar.selected_index
            self.meilisearch_settings.selected_index = self.selected_index
            self.delete_index.selected_index = self.selected_index
            self.data_load.selected_index = self.selected_index
        else:
            self.selected_index = None
            self.meilisearch_settings.selected_index = None
            self.delete_index.selected_index = None
            self.data_load.selected_index = None
            self.tabbed_content.active = "add-index"

    async def on_list_item__child_clicked(self, message: IndexSidebar.Selected) -> None:  # type: ignore[name-defined]
        self.selected_index = self.index_sidebar.selected_index
        self.meilisearch_settings.selected_index = self.index_sidebar.selected_index or ""
        self.delete_index.selected_index = self.index_sidebar.selected_index or None
        self.data_load.selected_index = self.index_sidebar.selected_index or None

    async def on_add_index_index_added(self) -> None:
        await self.index_sidebar.update()

    async def on_delete_index_index_deleted(self) -> None:
        await self.index_sidebar.update()
