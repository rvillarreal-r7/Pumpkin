#!/usr/bin/env python3

### external imports ###
import argparse

### local imports ###
from utils import logger
from device import device
from cli import cmdline
log = logger.LogAdapter()

# TODO: Cleanup
parser = argparse.ArgumentParser(description="Pumpkin", add_help=True)
tld_group = parser.add_mutually_exclusive_group(required=True)
tld_group.add_argument('--cmd', '-c', dest='cmd', action='store_true', help="Use the cmdline tooling")
tld_group.add_argument('--api', '-a',dest='api',action='store_true',help='Use the API server....running in headless mode')
tld_group.add_argument('--device','-d',dest='dev',action='store_true',help='Checking on devices')

second_group = parser.add_mutually_exclusive_group(required=True)
second_group.add_argument("--search", '-s',dest='searchTerm')
second_group.add_argument("--lookup", '-l',dest='lookupTerm')
args = parser.parse_args()

if args.cmd:
    log.debug("Starting cmdline mode")
    log.debug(args)
    # cmdline.search(args.searchTerm)
    if args.searchTerm:
        log.info("Performing a searching for an app")
        cmdline.search(args)
    else:
        log.debug("Already have the BundleID")
        cmdline.lookup(args)

elif args.api:
    log.debug("Running API headless mode")
    log.debug(args)

elif args.dev:
    log.debug("Loading Device Functions")
    dev = device.DeviceTool()
    dev.getDevicesInfo()

else:
    log.error("Ruh Roh Raggy")
    log.debug(args)
