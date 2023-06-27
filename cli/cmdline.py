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
    log.stack(args)
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
def devices(args):
    # eventually I could implement a REPL here for interactive management
    # but for now just testing two funcs. list and info
    connected_devices = device.Devices()
    if args.info:
        print("running info")
    elif args.list:
        connected_devices.list()
    else:
        log.fatal(__name__)
    # exit 
    utils.kbye(__name__)


def test():
    print("hello, world")