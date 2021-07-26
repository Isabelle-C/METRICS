#!/usr/bin/env python3

import click
from abmbiopsy.fibonacci import Fibonacci


@click.command()
@click.argument("number")
def cli(number):
    """CLI entrypoint for Fibonacci."""
    print(Fibonacci().calculate(number))


if __name__ == "__main__":
    cli()
