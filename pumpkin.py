#!/usr/bin/env python3
# This script has intentionally been left blank to prevent complications

def main():
	# setup logger early 
	from utils import logger
	logger.setup_logger()
	log = logger.LogAdapter()

	# parse args and dowork
	from cli import cmdline,args

if __name__ == "__main__":
	main()