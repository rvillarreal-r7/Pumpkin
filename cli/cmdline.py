#!/usr/bin/env python3

# This still needs to be abstracted to keep the cmdline tooling clean

### external imports ###
import sys,inspect

### local imports ###
from scrape import scrape
from utils import utils, logger
log = logger.LogAdapter()

def search(args):
    log.debug(__name__)
    tool = scrape.IPATool()
    data = tool.handleSearch(args)

def lookup(args):
    log.debug("User already knows the bundleID or AppID: %s" % args)
    tool = scrape.IPATool()
    tool.handleLookup(args)
    
    # For testing: assuming the user is going to download after this
    # I am also assuming the correct app has been chosen!! It's on you to not buy every
    # license for the app store
    tool.handleDownload(args)

    