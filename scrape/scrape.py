#!/usr/bin/python3
import inspect

# external imports
import requests
import time
import json
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# local imports
from scrape.reqs.store import *
from scrape.reqs.itunes import *

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter()

def get_zipinfo_datetime(timestamp=None):
    # Some applications need reproducible .whl files, but they can't do this without forcing
    # the timestamp of the individual ZipInfo objects. See issue #143.
    timestamp = int(timestamp or time.time())
    return time.gmtime(timestamp)[0:6]

def downloadFile(url, outfile):
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
                    log.info("Download progress: %3.2f%% (%5.1fM /%5.1fM)" % (
                    downLen / totalLen * 100, downLen / 1024 / 1024, totalLen / 1024 / 1024))
                    lastLen = downLen
    return outfile

class IPATool(object):
    log.debug("Creating IPATool Obj")
    def __init__(self):
        self.sess = requests.Session()

        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))

        self.appId = None
        self.appVerId = None
        self.jsonOut = None

    def searchApp(self, term=None, country="US", limit=10, media="software"):
        log.debug("Insider Search App")
        r = requests.get("https://itunes.apple.com/search?",
                            params={
                                "term": term,
                                "country": country,
                                "limit": limit,
                                "media": media,
                            },
                            headers={
                                "Content-Type": "application/x-www-form-urlencoded",
                            })
        # catch any errors with the responses and make sure it's not null
        try:
            try:
                data = json.loads(r.content)
            except:
                log.error('Decoding JSON has failed')
            results = int(data["resultCount"])
            if results > 0:
                return data
            else:
                log.info("No results returned from iTunes")
        except:
            log.error('Error converting to integer from string value')

    def handleLookup(self):
        log.debug("Current Func: %s()" % (inspect.stack()[0][3]))

