# Meilisearch TUI

[![Tests Status](https://github.com/sanders41/meilisearch-tui/workflows/Testing/badge.svg?branch=main&event=push)](https://github.com/sanders41/meilisearch-tui/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/meilisearch-tui/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/meilisearch-tui/main)
[![PyPI version](https://badge.fury.io/py/meilisearch-tui.svg)](https://badge.fury.io/py/meilisearch-tui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/meilisearch-tui?color=5cc141)](https://github.com/sanders41/meilisearch-tui)

A TUI (Text User Interface) for Managing and Searching with [Meilisearch](https://github.com/meilisearch/meilisearch)
from the terminal.

![Search](https://raw.githubusercontent.com/sanders41/meilisearch-tui/main/assets/search.gif)
![Settings](https://raw.githubusercontent.com/sanders41/meilisearch-tui/main/assets/settings.png)

## Installation

Installing with [pipx](https://github.com/pypa/pipx) is recommended.

```sh
pipx install meilisearch-tui
```

Alternatively Meilisearch TUI can be installed with pip.

```sh
pip install meilisearch-tui
```

## Usage

Start the TUI by running

```sh
meilisearch
```

If you are using Meilisearch v1.7.0+ you can optionally use hybrid search by starting by passing
the `-h` or `--hybrid-search` flag.

```sh
meilisearch -h
```

The first time you start the app you will need to enter the server address and master key (if using
one) into the configuration. If the `MEILI_HTTP_ADDR` and/or `MEILI_MASTER_KEY` environment variables
are set, these values will be used for the `meilisearch_url` and `master_key`.

If you have not already created an index and loaded data, first add an index on the Add Index tab of the Index Management screen. Then data can be loaded from the ‘Load Data` tab.

To search, click on the index in the sidebar you want to search on, by default the first index will
be selected. Then type the desired search.

## Contributing

Contributions to this project are welcome. If you are interested in contributing please see our [contributing guide](CONTRIBUTING.md)
