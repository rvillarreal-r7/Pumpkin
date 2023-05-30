#!/usr/bin/env python3
import codecs,frida

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

class FridaSession(object):
    def __init__(self,device):
        log.debug("Initializing FridaSession Obj")
        self.session = self.setupSession(device)

    def setupSession(self,device):
        try:
            return frida.get_device(device.identifier)
        except:
            log.fatal("Error getting FridaSession")

    def decrypt(self):
        print("decrypt")