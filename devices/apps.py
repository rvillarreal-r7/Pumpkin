#!/usr/bin/env python3

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

class AppsManager(object):
    def __init__(self):
        log.halt("Getting the App Manager for device: []")


class App(object):
    def __init__(self):
        log.halt("Getting the individual App from the App Manager")