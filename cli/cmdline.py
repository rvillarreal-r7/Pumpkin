#!/usr/bin/env python3
### external imports ###

### local imports ###
from scrape import scrape
from utils import utils

### local imports ####
from utils import logger
log = logger.LogAdapter()

def search(searchTerm):
    log.debug("Creating IPATool Obj in cmdline.py")
    tool = scrape.IPATool()
    data = tool.searchApp(term=searchTerm)
    choice = utils.parseData(data) # how to parse the data for now
    user_input = input("Start downloading [ %s ] ? [yes/no] " % choice['bundleId'])

    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']

    if user_input.lower() in yes_choices:
        handleDownload(choice)
    elif user_input.lower() in no_choices:
        print('user typed no')
    else:
        print('Type yes or no')


def handleDownload(choice):
    log.debug("handleDownload for %s " % choice['bundleId'])

def get_StoreClient():
    log.debug("auth")
