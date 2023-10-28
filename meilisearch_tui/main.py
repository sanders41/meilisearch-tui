from __future__ import annotations

import asyncio
import sys

from meilisearch_python_sdk.errors import MeilisearchCommunicationError
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer

from meilisearch_tui.client import get_client
from meilisearch_tui.config import Theme, load_config
from meilisearch_tui.errors import NoMeilisearchUrlError
from meilisearch_tui.screens.configuration import ConfigurationScreen
from meilisearch_tui.screens.indexes import IndexScreen
from meilisearch_tui.screens.search import SearchScreen
from meilisearch_tui.widgets.messages import ErrorMessage


def _is_uvloop_platform() -> bool:  # pragma: no cover
    if sys.platform != "win32":
        return True
    return False


class MeilisearchApp(App):
    BINDINGS = [
        ("s", "push_screen('search')", "Search"),
        ("i", "push_screen('index')", "Index Management"),
        ("c", "push_screen('configuration')", "Configuration"),
        ("ctrl+q", "app.quit", "Quit"),
    ]
    CSS_PATH = "meilisearch.css"
    TITLE = "Meilisearch"
    SCREENS = {
        "configuration": ConfigurationScreen(),
        "search": SearchScreen(),
        "index": IndexScreen(),
    }

    def compose(self) -> ComposeResult:
        with Container(id="body"):
            yield ErrorMessage("", classes="message-centered", id="generic-error")
        yield Footer()

    async def on_mount(self) -> None:
        config = load_config()
        if not config.meilisearch_url:
            self.push_screen("configuration")
        else:
            self.set_theme()
            try:
                async with get_client() as client:
                    indexes = await client.get_indexes()
                if indexes:
                    self.push_screen("search")
                else:
                    self.push_screen("index")
            except NoMeilisearchUrlError:
                self.push_screen("configuration")
            except MeilisearchCommunicationError as e:
                self.query_one(  # type: ignore
                    "#generic-error"
                ).renderable = f"An error occured: {e}.\nMake sure the Meilisearch server is running and accessable"
            except Exception as e:
                self.query_one("#generic-error").renderable = f"An error occured: {e}"  # type: ignore

    def set_theme(self) -> None:
        config = load_config()
        if config.theme == Theme.DARK:
            self.dark = True
        else:
            self.dark = False


def run_app() -> None:
    app = MeilisearchApp()
    app.run()


def main() -> int:
    if _is_uvloop_platform():  # pragma: no cover
        import uvloop

        if sys.version_info >= (3, 11):
            with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:  # type: ignore
                runner.run(run_app())  # type: ignore

        else:
            uvloop.install()  # type: ignore
            asyncio.run(run_app())  # type: ignore
    else:
        run_app()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
