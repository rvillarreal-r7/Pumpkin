#!/usr/bin/env python3
import logging

# create an obj for passing around
class LogAdapter(logging.LoggerAdapter):
    def __init__ (self, logger_name="Pumpkin", extra=None):
        self.logger = logging.getLogger(logger_name)
        self.extra = extra

    def info(self,msg):
        self.logger.info(msg)

    def debug(self,msg):
        self.logger.debug(msg)

    def warning(self,msg):
        self.logger.warning(msg)

    def error(self,msg):
        self.logger.error(msg)

def setup_logger(level=logging.DEBUG, log_to_file=False, log_prefix=None, logger_name='Pumpkin'):
    # define handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    
    # add formatter to handler
    handler.setFormatter(formatter)

    # get logger by name and add handler
    pumpkin_log = logging.getLogger(logger_name)
    pumpkin_log.propagate = False
    pumpkin_log.addHandler(handler)
    pumpkin_log.setLevel(logging.DEBUG)

    return pumpkin_log

