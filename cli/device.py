#!/usr/bin/env python3

# local imports
from utils import logger
log = logger.LogAdapter(__name__)
from cli.cli_common import Command

# external imports
import click

@click.group()
def cli():
    """device cli"""
    pass

@cli.group()
def device():
    """options"""
    pass
