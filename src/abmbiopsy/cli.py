#!/usr/bin/env python3

import click
from abmbiopsy.workflows import run_parse_simulations, run_calculate_stats


@click.group()
def cli() -> None:
    """
    TODO: add docstring
    """


@cli.command()
@click.argument("database")
@click.argument("simulation")
@click.option("-t", "--timepoint", default=1.0)
def parse_simulations(database: str, simulation: str, timepoint: float) -> None:
    """
    Parameters
    ----------
    database :
        File path to database file.
    simulation :
        File path to simulation file.
    timepoint :
        The timepoint to perform statistical test.
    """
    run_parse_simulations(database, simulation, timepoint)


@cli.command()
@click.argument("database")
@click.argument("simulation")
@click.argument("feature")
@click.option("-s", "--sample", default="punch")
@click.option("-t", "--timepoint", default=1.0)
@click.option("-r", "--radius", default=1)
def calculate_stats(
    database: str, simulation: str, feature: str, sample: str, timepoint: float, radius: int
) -> None:
    """
    Parameters
    ----------
    database :
        File path to database file.
    simulation :
        File path to simulation file.
    feature :
        The name of the feature for statistical test.
    sample : {"Needle", "needle", "punch", "Punch"}
        The type of the sample.
    radius :
        The radius of the punch sample and the width of the needle sample.
    timepoint :
        The timepoint to perform statistical test.
    """
    run_calculate_stats(database, simulation, feature, sample, timepoint, radius)


if __name__ == "__main__":
    cli()
