#!/usr/bin/env python3

def main():
	from utils import logger
	log = logger.LogAdapter(__name__)

	from cli import cmdline,args

if __name__ == "__main__":
	main()