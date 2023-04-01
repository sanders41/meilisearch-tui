from __future__ import annotations

import json
import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any


class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"


def _get_default_directory() -> Path:
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    settings_path = (
        Path(xdg_config) / "meilisearch-tui"
        if xdg_config
        else Path.home() / ".config" / "meilisearch-tui"
    )

    return settings_path.resolve()


class Config:
    get_default_directory = staticmethod(_get_default_directory)

    def __init__(
        self,
        meilisearch_url: str | None = None,
        master_key: str | None = None,
        *,
        timeout: int | None = None,
        theme: Theme = Theme.DARK,
    ) -> None:
        self.settings_dir = Config.get_default_directory()
        self.settings_file = self.settings_dir / "settings.json"
        self.meilisearch_url = meilisearch_url
        self.master_key = master_key
        self.timeout = timeout
        self.theme = theme

    def delete(self) -> None:
        if self.settings_file.exists():
            self.settings_file.unlink()

    def load(self) -> None:
        self.master_key = os.getenv("MEILI_MASTER_KEY", None)

        settings = None
        if self.settings_file.exists():
            with open(self.settings_file) as f:
                settings = json.load(f)

        if settings:
            self.meilisearch_url = settings.get("meilisearch_url", None)

            if settings.get("master_key"):
                self.master_key = settings["master_key"]

            self.timeout = settings.get("timeout", None)
            saved_theme = settings.get("theme", "dark")
            self.theme = Theme.DARK if saved_theme == "dark" else Theme.LIGHT

    def save(self) -> None:
        settings: dict[str, Any] = {}

        if not self.settings_dir.exists():
            self.settings_dir.mkdir(parents=True)

        if self.meilisearch_url:
            settings["meilisearch_url"] = self.meilisearch_url

        if self.master_key:
            settings["master_key"] = self.master_key

        if self.timeout:
            settings["timeout"] = self.timeout

        if self.theme:
            settings["theme"] = self.theme.value

        if settings:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)


@lru_cache(maxsize=1)
def load_config() -> Config:
    config = Config()
    config.load()
    return config


config = load_config()
