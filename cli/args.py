#!/usr/bin/env python3

### external imports ###
import argparse

### local imports ###
from utils import logger
from devices import device
from cli import cmdline
log = logger.LogAdapter(__name__)

# TODO: 
#  - Cleanup
#  - Add additional options
parser = argparse.ArgumentParser(description="Pumpkin", add_help=True)
tld_group = parser.add_mutually_exclusive_group(required=True)
tld_group.add_argument('--cmd', '-c', dest='cmd', action='store_true', help="Use the cmdline tooling")
tld_group.add_argument('--api', '-a',dest='api',action='store_true',help='Use the API server....running in headless mode')
tld_group.add_argument('--device','-d',dest='dev',action='store_true',help='Checking on devices')

second_group = parser.add_mutually_exclusive_group(required=True)
second_group.add_argument("--search", '-s',dest='searchTerm')
second_group.add_argument("--lookup", '-l',dest='lookupTerm')
args = parser.parse_args()

# Three core CLI options [cli,api,dev]
#  cli: run the tooling in CLI mode with local USB devices
#  api: run the tooling in headless mode
#  dev: diagnostics of connected USB devices
if args.cmd:
    log.debug("Starting cmdline mode")
    if args.searchTerm:
        cmdline.search(args)
    else:
        cmdline.lookup(args)

elif args.api:
    log.debug("Running API headless mode")
    log.halt("Todo")

elif args.dev:
    # log.debug("Loading Device Diagnostics")
    cmdline.devices(args)

else:
    log.error("Ruh Roh Raggy")
