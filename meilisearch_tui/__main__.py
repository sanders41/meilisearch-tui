from __future__ import annotations

from sys import platform

from textual.app import App

from meilisearch_tui.screens.connection_info import ConnectionInfo


def _is_uvloop_platform() -> bool:  # pragma: no cover
    if platform != "win32":
        return True
    return False


class MeilisearchApp(App):
    TITLE = "Meilisearch"

    # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    # BINDINGS = [("b", "push_screen('connection_info')", "ConnectionInfo")]

    def on_mount(self) -> None:
        self.install_screen(ConnectionInfo(), name="connection_info")
        self.push_screen("connection_info")

    # TITLE = "Meilisearch"

    # def compose(self) -> ComposeResult:
    #     """Create child widgets for the app."""
    #     yield Header()
    #     yield ConnectionInfo()
    #     yield Footer()

    # def action_toggle_dark(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.dark = not self.dark


def main() -> int:
    if _is_uvloop_platform():  # pragma: no cover
        import uvloop

        uvloop.install()

    app = MeilisearchApp()
    app.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
