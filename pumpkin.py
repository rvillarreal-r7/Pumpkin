#!/usr/bin/env python3
# This file is intentionally left blank to prevent complexities 

def main():
	# setup logger early 
	from utils import logger
	log = logger.LogAdapter(__name__)

	# parse args and dowork
	from cli import cmdline,args

if __name__ == "__main__":
	main()