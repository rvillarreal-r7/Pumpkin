#!/usr/bin/env python3

### local imports ###
from utils import logger
log = logger.LogAdapter(__name__)

# long list of imports
from cli import search as search_cli

### external imports ###
import click,logging

def set_verbosity(ctx, param, value):
    logger.update_logger(logging.DEBUG)

# command builder with the --verbose flag added
class Command(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params[:0] = [
            click.Option(('verbosity','-v', '--verbose'),is_flag=True, callback=set_verbosity),
        ]