from __future__ import annotations

from textual.app import RenderResult
from textual.widgets import Static


class ErrorMessage(Static):
    DEFAULT_CSS = """
    ErrorMessage {
        color: red;
        padding: 0 0 1 0;
    }
    """

    def render(self) -> RenderResult:
        return f"{self.renderable}"


class PageTitle(Static):
    DEFAULT_CSS = """
    PageTitle {
        text-align: center;
        padding-bottom: 2;
    }
    """

    def render(self) -> RenderResult:
        return f"{self.renderable}"


class SuccessMessage(Static):
    DEFAULT_CSS = """
    SuccessMessage {
        color: green;
    }
    """

    def render(self) -> RenderResult:
        return f"{self.renderable}"
