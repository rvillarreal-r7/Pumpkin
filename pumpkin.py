#!/usr/bin/env python3
import click

from cli.search import cli as search_cli

def cli():
    cli_commands = click.CommandCollection(sources=[search_cli])
    cli_commands.context_settings = dict(help_option_names=['-h', '--help'])
    cli_commands()


if __name__ == "__main__":
	cli()