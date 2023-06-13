#!/usr/bin/env python3

# external imports
from pick import pick
import sys, requests, time

# prepend all modules
from utils import utils, logger
log = logger.LogAdapter(__name__)


# input - self(obj)
# return - bool - is the port available? return True if we can use it and false if it's already blocked by another proc
def isPortAvail(port):
	# decided to pull this func out of the Device/Devices class because it doesn't really need those objects. and it's about the 
	# local device so it didn't feel "right"
	import socket
	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	status = (a_socket.connect_ex(("127.0.0.1", int(port))) != 0)
	if status:
		log.debug("isPort [%s] Avail? [%s]" % (port,status))
		return True
	else:
		return False

# input - self(obj)
# return - int - a random and available port within a specific range
def randPort():
    import random
    port = random.randint(60000,65000)
    while True:
        if isPortAvail(port):
            log.debug("Port [%i] is available" % (port))
            return port

# input - timestamp (time obj)
# return - time.gmtime (time obj)
def get_zipinfo_datetime(timestamp=None):
    log.debug("getting zipinfo datetime")
    # Some applications need reproducible .whl files, but they can't do this without forcing
    # the timestamp of the individual ZipInfo objects. See issue #143.
    timestamp = int(timestamp or time.time())
    return time.gmtime(timestamp)[0:6]

# input - url (str), outfile (str) - url of download, outfile where to write contents
# return - outfile (bytes?) - not sure I need this to be returned
def downloadFile(url, outfile):
    log.debug("Downloading file...")
    with requests.get(url, stream=True) as r:
        totalLen = int(r.headers.get('Content-Length', '0'))
        downLen = 0
        r.raise_for_status()
        with open(outfile, 'wb') as f:
            lastLen = 0
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):

                f.write(chunk)
                downLen += len(chunk)
                if totalLen and downLen - lastLen > totalLen * 0.05:
                    log.debug("Download progress: %3.2f%% (%5.1fM /%5.1fM)" % (
                    downLen / totalLen * 100, downLen / 1024 / 1024, totalLen / 1024 / 1024))
                    lastLen = downLen
    log.debug("Returning outfile of type [%s]" % type(outfile))
    return outfile

# input - options (list(strings)) - list of app options
# return - tuple[option(str), index(int)]
def chooseApp(options):
    title = "Which is the correct app?"
    option, index = pick(options, title, indicator='=>', default_index=0)
    return (option,index)

# input - msg (str) - Can be none as well as a string
# return - bool - User choice in True/False
def choice(msg=None) -> bool:
    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']
    if msg:
        user_input = input("%s [yes/no] " % (msg))
    else: # if no msg passed in a simple yes or no will suffice. 
        user_input = input("Continue? [yes/no] ")
    # check answer
    if user_input.lower() in yes_choices:
        return True
    elif user_input.lower() in no_choices:
        return False
    else:
        print('That is not an option try again') # fixme

# input - size_bytes (int)
# return - tuple[ s (str) size_name(str) ]
def convert_size(size_bytes):
   if size_bytes <= 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

# input - None
# return - None 
def kbye(caller=__name__):
    log.info("%s: kthxbye!" % caller)
    sys.exit()