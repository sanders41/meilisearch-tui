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
        semantic_ratio: float | None = None,
        embedder: str | None = None,
        config_dir: Path | None = None,
    ) -> None:
        self.config_dir = config_dir or Config.get_default_directory()
        self.settings_file = self.config_dir / "settings.json"
        self.meilisearch_url = meilisearch_url
        self._meilisearch_url_env_var = False
        self.master_key = master_key
        self._meilisearch_master_key_env_var = False
        self.timeout = timeout
        self.theme = theme
        self.semantic_ratio = semantic_ratio
        self.embedder = embedder

    def delete(self) -> None:
        if self.settings_file.exists():
            self.settings_file.unlink()

    def load(self) -> None:
        settings = None
        if self.settings_file.exists():
            with open(self.settings_file) as f:
                settings = json.load(f)

        if settings:
            if settings.get("meilisearch_url"):
                self.meilisearch_url = settings["meilisearch_url"]

            if settings.get("master_key"):
                self.master_key = settings["master_key"]

            self.timeout = settings.get("timeout", None)
            saved_theme = settings.get("theme", "dark")
            self.theme = Theme.DARK if saved_theme == "dark" else Theme.LIGHT
            self.semantic_ratio = settings.get("semantic_ratio")
            self.embedder = settings.get("embedder")

        if os.getenv("MEILI_HTTP_ADDR", None):
            self.meilisearch_url = os.getenv("MEILI_HTTP_ADDR")
            self._meilisearch_url_env_var = True
        else:
            self._meilisearch_url_env_var = False

        if os.getenv("MEILI_MASTER_KEY", None):
            self.master_key = os.getenv("MEILI_MASTER_KEY")
            self._meilisearch_master_key_env_var = True
        else:
            self._meilisearch_master_key_env_var = False

    def save(self) -> None:
        settings: dict[str, Any] = {}

        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)

        if self.meilisearch_url and not self._meilisearch_url_env_var:
            settings["meilisearch_url"] = self.meilisearch_url

        if self.master_key and not self._meilisearch_master_key_env_var:
            settings["master_key"] = self.master_key

        if self.timeout:
            settings["timeout"] = self.timeout

        if self.theme:
            settings["theme"] = self.theme.value

        if self.semantic_ratio:
            settings["semantic_ratio"] = self.semantic_ratio

        if self.embedder:
            settings["embedder"] = self.embedder

        if settings:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)


@lru_cache(maxsize=1)
def load_config(config_dir: Path | None = None) -> Config:
    config = Config(config_dir=config_dir)
    config.load()
    return config
