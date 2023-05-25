#!/usr/bin/env python3
import logging

# create an obj for passing around
class LogAdapter(logging.LoggerAdapter):
    def __init__ (self,logger_name):
        self.logger = setup_logger(logger_name=logger_name)

    def info(self,msg):
        self.logger.info(msg)

    def debug(self,msg):
        self.logger.debug(msg)

    def warning(self,msg):
        self.logger.warning(msg)

    def error(self,msg):
        self.logger.error(msg)
    
    def fatal(self,msg):
        self.logger.fatal(msg)
        from utils import utils
        utils.kbye()

    def halt(self,msg):
        self.logger.warning("HALTED: %s " % msg)
        input("Press [Enter] to continue")
        
    def getLevel(self):
        return self.logger.level

def setup_logger(level=logging.DEBUG, log_to_file=False, log_prefix=None, logger_name=__name__):
    # define handler and formatter
    handler = logging.StreamHandler()
    # change formatting and look here.
    formatter = logging.Formatter("%(levelname)s - [%(name)s] - %(message)s")

    # add formatter to handler
    handler.setFormatter(formatter)

    # get logger by name and add handler
    pumpkin_log = logging.getLogger(logger_name)
    pumpkin_log.propagate = False
    pumpkin_log.addHandler(handler)
    pumpkin_log.setLevel(level)

    return pumpkin_log
