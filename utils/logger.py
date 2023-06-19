#!/usr/bin/env python3
import logging,inspect,traceback
from colored import fg, bg, attr

# define the color scheme
# ORANGE for funsies and highlighting. 
# LIGHT_GRAY for detailed info that needs attention
# GRAY for background info, important but not attention grabbing important
# MOLLY black
ORANGE=fg(209)
LIGHT_GRAY=fg(250)
GRAY=fg(245)
MOLLY=fg(0)

# create an obj for passing around
class LogAdapter(logging.LoggerAdapter):
    def __init__ (self,logger_name,level=logging.INFO): # defaults to INFO output
        self.logger = setup_logger(logger_name=logger_name, level=level) # passes the level which by default info

    def info(self,msg,color=True):
        # build the msg # later add a color.False
        if color:
            output = f'{LIGHT_GRAY}{msg}'
            print(output)
        else:
            print("only color supported at this time")

    def debug(self,msg=None,data=None):
        self.logger.debug(msg)

    def warning(self,msg):
        self.logger.warning(msg)

    def error(self,msg):
        self.logger.error(msg)
    
    def fatal(self,msg=None):
        if msg != None:
            self.logger.fatal(f'{msg}') 
        self.kbye() # panic exit

    def halt(self,msg):
        self.logger.warning(f"{LIGHT_GRAY}HALTED: {msg}")
        input(f"{LIGHT_GRAY}Press [Enter] to continue") # don't panic exit

    def stack(self,data):
        # initialize the inspect obj
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        print(f'{GRAY}{frame}')
        
        # for line in stack trace print in a light gray with info slightly lighter. 
        for item in stack_trace:
            print(f"{fg(245)}stack_trace: {fg(247)}{item.strip()}")
        # as long as the data passed into the stack trace func isn't null we can print info about it. 
        if data != None:
            print(f"{GRAY}Type: {LIGHT_GRAY}{type(data)}")
            print(f"{GRAY}Data: {LIGHT_GRAY}{data}")
            print(f"{GRAY}Props: {LIGHT_GRAY}{dir(data)}")
            properties = vars(data)                 # Get the dictionary of object properties
            for prop, value in properties.items():  # loop through printing the props and values
                print(f"{GRAY}Property: [{LIGHT_GRAY}{prop}{GRAY}] - Value: {LIGHT_GRAY}{value}")
        # add a choice here to dump back to the cmdline
        yes_choices = ['yes', 'y']
        no_choices = ['no', 'n']
        user_input = input(f"{LIGHT_GRAY}Continue to pdb? [yes/no] ")
        if user_input in yes_choices:
            # set the output back to "normal" which is our light_gray
            from pdb import set_trace as bp
            bp() # will drop the user into pdb shell with light gray text

    def getLevel(self):
        return self.logger.level

    def kbye(self):
        self.logger.fatal("Panic!")
        import sys; sys.exit()

def update_logger(level) -> None:
        # Get the root logger
        root_logger = logging.getLogger()

        # Set the new logging level for the root logger
        root_logger.setLevel(level)

        # Iterate over all existing loggers and set the new logging level
        for logger_name in logging.Logger.manager.loggerDict.keys():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)


def setup_logger(level=logging.INFO, log_to_file=False, log_prefix=None, logger_name=__name__):
    # define handler and formatter
    handler = logging.StreamHandler()
    # change formatting and look here.
    formatter = logging.Formatter("[%(name)s] - %(message)s")

    # add formatter to handler
    handler.setFormatter(formatter)

    # get logger by name and add handler
    pumpkin_log = logging.getLogger(logger_name)
    pumpkin_log.propagate = False
    pumpkin_log.addHandler(handler)
    pumpkin_log.setLevel(level)

    return pumpkin_log
