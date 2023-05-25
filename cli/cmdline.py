#!/usr/bin/env python3

# prepend all modules
from utils import utils, logger
log = logger.LogAdapter(__name__)

### local imports ###
from scrape import downloader
from devices import device

# input - args (argparse obj)
# return - None
def search(args):
    dl = downloader.IPATool(args)
    
    if dl.handleSearch():
        dl.handleInstall()
    else:
        utils.kbye(__name__)

# input - args (argparse obj)
# return - None
def lookup(args):
    dl = downloader.IPATool(args)

    if dl.handleLookup():
        dl.handleInstall()
    else:
        utils.kbye(__name__)

# input - args (argparse obj)
# return - None
def devices(args=None):
    log.debug("Args provided. Run management tooling")
    log.halt("Implement Device Management - fixme")
    utils.kbye(__name__)