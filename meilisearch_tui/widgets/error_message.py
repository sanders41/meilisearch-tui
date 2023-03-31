from __future__ import annotations

from textual.app import RenderResult
from textual.widgets import Static


class ErrorMessage(Static):
    DEFAULT_CSS = """
    ErrorMessage {
        color: red;
    }
    """

    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def render(self) -> RenderResult:
        return f"{self.error_message}"
