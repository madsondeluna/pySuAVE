"""
Command-line interface for pySuAVE tools.

This module provides the main CLI entry point using Click.
"""

import click
from pysuave.core.constants import VERSION


@click.group()
@click.version_option(version=VERSION, prog_name="pySuAVE")
def main():
    """
    pySuAVE - Surface Assessment Via grid Evaluation (Python version)
    
    A suite of tools for analyzing molecular surfaces and membranes.
    """
    pass


# Import subcommands
from pysuave.cli.stat import stat_command

# Register commands
main.add_command(stat_command)


if __name__ == '__main__':
    main()
