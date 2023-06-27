#!/usr/bin/env python3

from utils import logger
log = logger.LogAdapter(__name__)

from cli.cli_common import Command

# external imports
import click

@click.group()
def cli():
    """ apps cli """
    pass


@cli.group()
def apps():
    """ application options """
    pass


@apps.command('list', cls=Command)
@click.option('--color/--no-color', default=True)
@click.option('-u', '--user', is_flag=True, help='include user apps')
@click.option('-s', '--system', is_flag=True, help='include system apps')
@click.option('--hidden', is_flag=True, help='include hidden apps')
def apps_list(color, user, system, hidden):
    """ list installed apps """


# @search.command('list', cls=Command)
# @click.option('--color/--no-color', default=True)
# @click.option('-u', '--user', is_flag=True, help='include user apps')
# @click.option('-s', '--system', is_flag=True, help='include system apps')
# @click.option('--hidden', is_flag=True, help='include hidden apps')
# def apps_list(verbosity):
#     """ list installed apps """
#     print('hello')