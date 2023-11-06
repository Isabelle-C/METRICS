# METRICS

[![Build Status](https://github.com/bagherilab/METRICS/workflows/build/badge.svg)](https://github.com/bagherilab/METRICS/actions?query=workflow%3Abuild)
[![Lint Status](https://github.com/bagherilab/METRICS/workflows/lint/badge.svg)](https://github.com/bagherilab/METRICS/actions?query=workflow%3Alint)
[![Documentation](https://github.com/bagherilab/METRICS/workflows/documentation/badge.svg)](https://bagherilab.github.io/METRICS/)


## Getting started

1. Clone the repo.

2. Activate the environment.

```bash
$ poetry shell
```

3. Install dependencies.

```bash
$ poetry install
```

4. Run the CLI.

```bash
$ python3 src/main.py
```
 
## Setup Information
This repository is uses the following tools:

- [Poetry](https://python-poetry.org/) for packaging and dependency management
- [Tox](https://tox.readthedocs.io/en/latest/) for automated testing
- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [Pylint](https://www.pylint.org/) for linting

as well as GitHub Actions to automatically build, test, lint, and generate documentation.

## General commands

The `Makefile` include three commands for working with the project.

- `make clean` will clean all the build and testing files
- `make build` will run tests and lint your code (you can also just run `tox`)
- `make docs` will generate documentation
