#!/usr/bin/env python3

### local imports ###
from cli import cmdline
from utils import logger
log = logger.LogAdapter(__name__)

### external imports ###
import argparse,logging

# Create the top-level parser
parser = argparse.ArgumentParser(description="Pumpkin", add_help=True)
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# Create the parser for the "cmd" command
cmd_parser = subparsers.add_parser('cmd', help='Execute the cmdline tooling')
cmd_parser.add_argument('--verbose', '-v', action='store_true') # I really hate this...
cmd_subparser = cmd_parser.add_mutually_exclusive_group(required=True)
cmd_subparser.add_argument('--search','-s', dest='searchTerm', help='Search the AppStore for a bundleId')
cmd_subparser.add_argument('--lookup','-l',dest='lookupTerm', help='Lookup App by bundleId [com.example.App]',)

# Create the parser for the "api" command
api_parser = subparsers.add_parser('api', help='Execute the API server')
api_parser.add_argument('--verbose', '-v', action='store_true') # I really hate this...
api_subparser = api_parser.add_mutually_exclusive_group()
api_subparser.add_argument('--info', action='store_true', help='Get list of connected devices',)

# Create the parser for the "device" command
device_parser = subparsers.add_parser('device', help='Perform device operations')
device_parser.add_argument('--verbose', '-v', action='store_true') # I really hate this...
device_subparser = device_parser.add_mutually_exclusive_group(required=True)
device_subparser.add_argument('--info',action='store_true', help='Get list of connected devices')
device_subparser.add_argument('--list',action='store_true', help='Get list of connected devices')

# Parse the command-line arguments
args = parser.parse_args()

if args.verbose:
    logger.update_logger(logging.DEBUG) # if we have verbose flag increease logging level

if args.command:
    # Three core CLI options [cli,api,dev]
    if args.command == 'cmd':
        log.debug("Starting cmdline mode")
        if args.searchTerm:
            cmdline.search(args)
        else:
            cmdline.lookup(args)

    elif args.command == 'api':
        log.halt("Running API headless mode")

    elif args.command == 'device':
        # log.debug("Loading Device Diagnostics")
        cmdline.devices(args)
    else:
        log.error("Ruh Roh Raggy")
else:
    log.error("Pumpkin expects at least one command")
    parser.print_help()
