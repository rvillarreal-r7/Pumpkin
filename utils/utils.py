#!/usr/bin/env

# temp logging
from pick import pick
import sys
import json

# prepend all scripts with logger object retrieval
# from utils import logger
# log = logger.getLogger(__name__)
import logging
log = logging.getLogger(__name__)

def parseData(data):
    log.info("parsing data")
    try:
        results = int(data["resultCount"])
    except:
        log.debug('Error converting resultCount to integer from string value')
        log.debug("Data: ") # had to remove data because it was empty
        log.debug("Exiting")
        sys.exit()

    options = []
    for app in data["results"]:
        # adding the names to a list for the cmdline picker
        options.append(app["trackName"] + " - " + app["bundleId"] + " - v" + app["version"])

    title = "Which is the correct app?"
    option, index = pick(options, title, indicator='=>', default_index=0)
    
    return (data["results"][index])

def get_zipinfo_datetime(timestamp=None):
    log.debug("getting zipinfo datetime")
    # Some applications need reproducible .whl files, but they can't do this without forcing
    # the timestamp of the individual ZipInfo objects. See issue #143.
    timestamp = int(timestamp or time.time())
    return time.gmtime(timestamp)[0:6]


def downloadFile(url, outfile):
    log.debug("downloading file")
    with requests.get(url, stream=True) as r:
        totalLen = int(r.headers.get('Content-Length', '0'))
        downLen = 0
        r.raise_for_status()
        with open(outfile, 'wb') as f:
            lastLen = 0
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
                downLen += len(chunk)
                if totalLen and downLen - lastLen > totalLen * 0.05:
                    logger.info("Download progress: %3.2f%% (%5.1fM /%5.1fM)" % (
                    downLen / totalLen * 100, downLen / 1024 / 1024, totalLen / 1024 / 1024))
                    lastLen = downLen
    return outfile