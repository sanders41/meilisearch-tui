# Meilisearch TUI

[![Tests Status](https://github.com/sanders41/meilisearch-tui/workflows/Testing/badge.svg?branch=main&event=push)](https://github.com/sanders41/meilisearch-tui/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/meilisearch-tui/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/meilisearch-tui/main)
[![PyPI version](https://badge.fury.io/py/meilisearch-tui.svg)](https://badge.fury.io/py/meilisearch-tui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/meilisearch-tui?color=5cc141)](https://github.com/sanders41/meilisearch-tui)

A TUI for Managing and Searching with [Meilisearch](https://github.com/meilisearch/meilisearch).

![Search](https://raw.githubusercontent.com/sanders41/meilisearch-tui/main/assets/search.gif)

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

start with TUI by running

```sh
meilisearch
```

The first time you start the app you will need to enter the server address and master key (if using
one) into the configuration. If the `MEILI_MASTER_KEY` environment variable is set, the app is
able to get the master key from this.

If you have not already created an index and loaded data, this can be done from the `Load Data`
screen. Specifying an `Index` here will create the index if it does not already exist. Indexes
that have already been created will show at the bottom of the screen. By default the first index
will auto-populate the `Index` box.

To search, enter the index you want to search on, by default the first index found will pre-populate
the box. Then type the desired search.

## Contributing

Contributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)
