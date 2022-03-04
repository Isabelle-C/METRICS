#!/usr/bin/env python3

import click
from abmbiopsy.workflows import run_parse_simulations, run_calculate_stats


@click.group()
def cli():
    """
    TODO: add docstring
    """


@cli.command()
@click.argument("database")
@click.argument("simulation")
@click.option("-t", "--timepoint", default=1.0)
def parse_simulations(database, simulation, timepoint):
    """
    TODO: add docstring
    """
    run_parse_simulations(database, simulation, timepoint)


@cli.command()
@click.argument("database")
@click.argument("simulation")
@click.argument("feature")
@click.option("-s", "--sample", default="punch")
@click.option("-r", "--radius", default=1)
@click.option("-t", "--timepoint", default=1.0)
def calculate_stats(database, simulation, feature, sample, radius, timepoint):
    """
    TODO: add docstring
    """
    run_calculate_stats(database, simulation, feature, sample, radius, timepoint)


if __name__ == "__main__":
    cli()
