#!/usr/bin/env python3

### external imports ###
import argparse,logging

### local imports ####
from utils import logger

if __name__ == "__main__":
	logger.setup_logger()
	log = logger.LogAdapter()

	# I will eventually need to clean this up, but for now i'm going to use this as my playground
	parser = argparse.ArgumentParser(description="Pumpkin", add_help=True)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--cmd', '-c', dest='cmd', action='store_true', help="Use the cmdline tooling")
	group.add_argument('--api', '-a',dest='api', action='store_true',help='Use the API server....running in headless mode')

	parser.add_argument("--search", '-s', dest='searchTerm')
	args = parser.parse_args()
	
	if args.cmd:
		log.debug("Starting cmdline mode")
		from cli import cmdline
		cmdline.search(args)

	if args.api:
		log.debug("Running API headless mode")