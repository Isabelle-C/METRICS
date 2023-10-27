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

## Config Setup
```

```

## Data Information

Data and results for `POPULATION_HETEROGENEITY` simulations.
Simulations conditions include context, population mixture, population heterogeneity, and background heterogeneity.

__AUTHOR__ . Jessica S. Yu

__DATE__ . November 2019

__TAGS__ . agent-based model, ARCADE, population heterogeneity, crowding tolerance, metabolic preference, migratory threshold

__MODEL__ . [ARCADE v2.2](https://github.com/bagherilab/ARCADE/releases/tag/v2.2)

- [`POPULATION_HETEROGENEITY_C.xml`](https://github.com/bagherilab/arcade_emergent_behavior/blob/main/setups/POPULATION_HETEROGENEITY_C.xml)
- [`POPULATION_HETEROGENEITY_CH.xml`](https://github.com/bagherilab/arcade_emergent_behavior/blob/main/setups/POPULATION_HETEROGENEITY_CH.xml)

__DESCRIPTION__ . Simulations of all possible permutations of four populations (X, A, B, C) under colony and tissue context with different levels of parameter heterogeneity (0, 0.1, 0.2, 0.3, 0.4, and 0.5).
For tissue context, the healthy cell populations also varies parameter heterogeneity independent of the cancerous cell populations.
Each condition is run for 15 days (21600 ticks) with 20 replicates (random seeds 0 - 19).
Cells are introduced to the center of the constant source environment after a 1 day delay.
Snapshots are taken every 0.5 days (720 ticks).

The `data/` folder contains `.tar.xz` compressed replicate sets.
The `data.param/` folder contains `.tar.xz` compressed replicate sets for `.PARAM` output.
The `results/` folder contains `.pkl` files of data parsed into arrays.

Simulations are labeled as: `[context]_[populations]_[population heterogeneity]_[background heterogeneity]`

- `[context]`
    - `C` = colony context, cancerous cell populations only
    - `CH` = tissue context, cancerous cell populations and healthy cells
- `[populations]`
    - `X` = cancerous cell population with basal parameters
    - `A` = cancerous cell population with `max_height` x 1.5
    - `B` = cancerous cell population with `meta_pref` x 1.5
    - `C` = cancerous cell population with `migra_threshold` x 0.5
- `[population heterogeneity]`
    - `##` = heterogeneity value for cancerous cell populations (`##`/10)
- `[background heterogeneity]`
    - `##` = heterogeneity value for healthy cell population (`##`/10)
 
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
