#!/usr/bin/env python3
import unittest
from click.testing import CliRunner
from src.abmbiopsy.cli import cli


class TestCLI(unittest.TestCase):
    """Functional tests for abmbiopsy CLI."""

    def test_cli_prints_nth_fibonacci_number_and_exits_0(self):
        # User passes number to program.
        commands = ["42"]

        # Program calls CLI.
        runner = CliRunner()
        result = runner.invoke(cli, commands)

        # Check exit code
        self.assertEqual(result.exit_code, 0)

        # ...and output value.
        self.assertEqual(result.output.strip(), "267914296", "first check failed")
