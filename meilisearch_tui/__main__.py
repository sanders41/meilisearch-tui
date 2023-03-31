from __future__ import annotations

from sys import platform

from textual.app import App

from meilisearch_tui.config import Theme, config
from meilisearch_tui.screens.configuration import ConfigurationScreen
from meilisearch_tui.screens.data_load import DataLoadScreen
from meilisearch_tui.screens.index import AddIndexScreen
from meilisearch_tui.screens.search import SearchScreen


def _is_uvloop_platform() -> bool:  # pragma: no cover
    if platform != "win32":
        return True
    return False


class MeilisearchApp(App):
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("s", "push_screen('search')", "Search"),
        ("d", "push_screen('data_load')", "Load Data"),
        ("a", "push_screen('add_index')", "Add Index"),
        ("c", "push_screen('configuration')", "Configuration"),
    ]
    CSS_PATH = "meilisearch.css"
    TITLE = "Meilisearch"
    SCREENS = {
        "configuration": ConfigurationScreen(),
        "add_index": AddIndexScreen(),
        "search": SearchScreen(),
        "data_load": DataLoadScreen(),
    }

    # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def on_mount(self) -> None:
        if not config.meilisearch_url:
            self.push_screen("configuration")
        else:
            self.set_theme()
            self.push_screen("add_index")

    def set_theme(self) -> None:
        if config.theme == Theme.DARK.value:
            self.dark = True
        else:
            self.dark = False


def main() -> int:
    if _is_uvloop_platform():  # pragma: no cover
        import uvloop

        uvloop.install()

    app = MeilisearchApp()
    app.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
