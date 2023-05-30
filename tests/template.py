#!/usr/bin/env python3

# [] indicates user input needed
#import <package>

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

# class [Classname](object):
#     def __init__(self,[params]):
#         log.debug("")
#     def foo(self,[params] -> bool):
#         log.info("inside foo")


def main():
    print("main")

if __name__ == "__main__":
    main()
