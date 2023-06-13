#!/usr/bin/env python3

# prepend all modules
from utils import utils, logger
log = logger.LogAdapter(__name__)

uploaded = []
mimes = {
        '.apk': 'application/octet-stream',
        '.ipa': 'application/octet-stream',
        '.appx': 'application/octet-stream',
        '.zip': 'application/zip',
    }

# create an obj for passing around
class Mob(object):
    def __init__ (self):
        log.halt("Setting Up MobSF Connection")
        

    
