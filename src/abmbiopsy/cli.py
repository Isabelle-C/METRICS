#!/usr/bin/env python3

import click


@click.group()
def cli():
    pass


@cli.command()
def sample():
    """
    Workflow for sampling biopsies from simulated tumor data.

    Examples
    --------
    Run needle biopsy of radius 3 on simulation set X for timepoint 4:
    $ python cli.py sample X.tar.xz --sample_shape needle --sample_size 3 --time 4 /path/to/output/

    Run all punch biopsies between radii 2 and 5 for simulation set Y for all timepoints:
    $ python cli.py sample Y.tar.xz --sample_shape punch --sample_size 2-5 --time * /path/to/output/

    Run needle biopsy of radius < 5 on all simulations sets in folder Z for timepoint 6:
    $ python cli.py sample /path/to/Z/ --sample_shape needle --sample_size <5 --time 6 /path/to/output/

    """
    pass


@cli.command()
def stats():
    """
    Workflow for statistical testing on features of simulated tumor sample data.

    Examples
    --------
    Calculate stats for features X + Y:
    $ python cli.py stats /path/to/biopsy/files/ /path/to/tumor/files/ --feature X,Y /path/to/stats/files/

    Calculate stats for all features:
    $ python cli.py stats /path/to/biopsy/files/ --feature * /path/to/stats/files/

    Calculate stats for feature Z on a single biopsy file A compared to tumor file B:
    $ python cli.py stats biopsy_file_a tumor_sample_b --feature Z /path/to/stats/files/

    """
    pass


if __name__ == "__main__":
    cli()
