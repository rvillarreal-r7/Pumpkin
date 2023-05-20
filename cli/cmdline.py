#!/usr/bin/env python3

# This still needs to be abstracted to keep the cmdline tooling clean

### external imports ###
import sys,inspect

### local imports ###
from scrape import scrape
from device import device

from utils import utils, logger
log = logger.LogAdapter()

def search(args): 
    log.debug(__name__)
    tool = scrape.IPATool()
    tool.handleSearch(args)

def lookup(args):
    log.debug("User already knows the bundleID or AppID: %s" % args.lookupTerm)
    tool = scrape.IPATool()
    tool.handleLookup(args)

    # For Testing: I am assuming the download has already completed
    # tool.handleLookup will perform the lookup of the bundleId and will download directly instead of 
    # letting the user choose a download option. because yeah they already chose
    # so if everything goes to plan we should now call handleDownload() from the handleLookup()
    # inside handleDownload() we will get the filepath which is the ./[output-dir] + [bundleID + "-" + app_ver].ipa
    # at that point we should be ready for install right?
    # using the app [bundleId=com.facebook.Facebook]
    tool.filepath = "./downloads/com.facebook.Facebook-415.1.ipa" # remove after testing
    tool.handleInstall(args)

def devices(args):
    # used for testing
    log.debug("Checking on devices")
    device.test()