# Python project template repository

[![Build Status](https://github.com/aprybutok/abm_biopsy/workflows/build/badge.svg)](https://github.com/aprybutok/abm_biopsy/actions?query=workflow%3Abuild)
<!-- [![Codecov](https://img.shields.io/codecov/c/gh/jessicasyu/sandbox?token=YQTHAS0315)](https://codecov.io/gh/jessicasyu/sandbox) -->
[![Lint Status](https://github.com/aprybutok/abm_biopsy/workflows/lint/badge.svg)](https://github.com/aprybutok/abm_biopsy/actions?query=workflow%3Alint)
[![Documentation](https://github.com/aprybutok/abm_biopsy/workflows/documentation/badge.svg)](https://aprybutok.github.io/abm_biopsy/)

This repository is a template for Python projects that uses the following tools:

- [Poetry](https://python-poetry.org/) for packaging and dependency management
- [Tox](https://tox.readthedocs.io/en/latest/) for automated testing
- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [Pylint](https://www.pylint.org/) for linting

as well as GitHub Actions to automatically build, test, lint, and generate documentation.

## Getting started

1. Clone the repo.
2. Initialize the repository with Poetry by running:

```bash
$ poetry init
```

3. Install dependencies.

```bash
$ poetry install
```

4. Activate the environment.

```bash
$ poetry shell
```

5. Run the CLI.

```bash
$ python src/sandbox/cli.py 10
55
```

## General commands

The `Makefile` include three commands for working with the project.

- `make clean` will clean all the build and testing files
- `make build` will run tests and lint your code (you can also just run `tox`)
- `make docs` will generate documentation
