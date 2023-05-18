#!/usr/bin/python3
import inspect
import getpass

# external imports
import requests
import plistlib
import os
import zipfile
import time
from pick import pick
import json
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import urllib.parse

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
    log.debug("Downloading file...")
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
    log.debug("Returning outfile")
    return outfile

class IPATool(object):
    def __init__(self):
        log.debug("Initializing IPATool Obj")
        self.sess = requests.Session()

        self.appId = None
        self.appVerId = None
        
        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    
    def _outputJson(self, obj):
        self.jsonOut = obj

    def _handleStoreException(self, _e):
        e = _e # type: StoreException
        log.fatal("Store %s failed! Message: %s%s" % (e.req, e.errMsg, " (errorType %s)" % e.errType if e.errType else ''))
        log.fatal("    Raw Response: %s" % (e.resp.as_dict()))

    def _get_StoreClient(self, args):
        Store = StoreClient(self.sess)

        appleid = args.appleid
        applepass = args.password

        log.info("Logging into iTunes...")

        Store.authenticate(appleid, applepass)
        log.info('Logged in as %s' % Store.accountName)
        return Store

    def handleLookup(self, args):
        log.debug("Current Func: %s()" % (inspect.stack()[0][3]))
        # this needs to be a valid bundle or AppID otherwise it will fail
        # for testing assuming it's valid com.facebook.Facebook
        log.debug("BundleID/AppID: %s" % args.lookupTerm)
        args.country = "US"
        args.bundle_id = args.lookupTerm
        args.appId = None

        #everything above to the func def for testing purposes - define any vars above
        if args.bundle_id:
            s = 'BundleID: %s' % args.bundle_id
        else:
            s = 'AppID: %s' % args.appId
        log.info('Looking up app in country "%s" with %s' % (args.country, s))
        iTunes = iTunesClient(self.sess)

        appInfos = iTunes.lookup(bundleId=args.bundle_id, appId=args.appId, country=args.country)
        
        if appInfos.resultCount != 1:
            log.fatal("Failed to find app in country %s with %s" % (args.country, s))
            return
        
        appInfo = appInfos.results[0]
        log.debug("Found app:\n\tName: %s\n\tVersion: %s\n\tbundleId: %s\n\tappId: %s" % (appInfo.trackName, appInfo.version, appInfo.bundleId, appInfo.trackId))
        self.appId = appInfo.trackId
        self.appInfo = appInfo

    def handleDownload(self,args):
        log.debug("Current Func: %s()" % (inspect.stack()[0][3]))
        args.appId = None
        args.appVerId = None
        #args.appleid = input("username: ")
        log.debug("Get Username/PW")
        args.output_dir = "."
        args.appleid = input("Username: ")
        args.password = getpass.getpass()

        #everything above to the func def for testing purposes - define any vars above
        if args.appId:
            self.appId = args.appId
        if args.appVerId:
            self.appVerId = args.appVerId
        if not self.appId:
            log.fatal("appId not supplied!")
            return

        try:
            log.debug("Attempting Apple Store Auth..")
            appleid = args.appleid
            Store = self._get_StoreClient(args)
            try:
                log.debug("Attempting to Purchase %s License" % self.appInfo.bundleId)
                Store.purchase(self.appId)
            except StoreException as e:
                if e.errMsg == 'purchased_before':
                    log.warning('You have already purchased appId %s before' % (self.appId))
                    # this is fine, continue
                else:
                    raise # we shouldn't get here?
            log.info('Retriving download info for appId %s%s' % (self.appId, " with versionId %s" % self.appInfo.version))

            downResp = Store.download(self.appId, self.appVerId)
            log.debug(downResp)
            if not downResp.songList:
                log.fatal("Failed to get app download info!")
                raise StoreException('download', downResp, 'no songList')
            downInfo = downResp.songList[0]

            appName = downInfo.metadata.bundleDisplayName
            appId = downInfo.songId
            appBundleId = downInfo.metadata.softwareVersionBundleId
            appVerId = downInfo.metadata.softwareVersionExternalIdentifier
            appVer = downInfo.metadata.bundleShortVersionString

            log.debug(appName)
            log.debug(appId)
            log.debug(appBundleId)
            log.debug(appVerId)
            log.debug(appVer)
            log.info(f'Downloading app {appName} ({appBundleId}) with appId {appId} (version {appVer}, versionId {appVerId})')


            filename = '%s-%s.ipa' % (appBundleId,
                                            appVer,)
            log.debug("File Output: %s" % filename)
            filepath = os.path.join(args.output_dir, filename)
            log.debug("File Path: %s" % filepath)

            log.info("Downloading IPA to %s" % filepath)
            downloadFile(downInfo.URL, filepath)
            with zipfile.ZipFile(filepath, 'a') as ipaFile:
                log.info("Writing out iTunesMetadata.plist...")
                metadata = downInfo.metadata.as_dict()
                if appleid:
                    metadata["apple-id"] = appleid
                    metadata["userName"] = appleid
                ipaFile.writestr(zipfile.ZipInfo("iTunesMetadata.plist", get_zipinfo_datetime()), plistlib.dumps(metadata))

                appContentDir = [c for c in ipaFile.namelist() if c.startswith('Payload/') and len(c.strip('/').split('/')) == 2][0]
                appContentDir = appContentDir.rstrip('/')

                scManifestData = ipaFile.read(appContentDir + '/SC_Info/Manifest.plist')
                scManifest = plistlib.loads(scManifestData)

                sinfs = {c.id: c.sinf for c in downInfo.sinfs}
                for i, sinfPath in enumerate(scManifest['SinfPaths']):
                    ipaFile.writestr(appContentDir + '/' + sinfPath, sinfs[i])
            log.info("Downloaded ipa to %s" % filename)
        ##############################    
        except StoreException as e:
            self._handleStoreException(e)

    def handleSearch(self,args):
        log.debug("Current Func: %s()" % (inspect.stack()[0][3]))
        log.debug(args)
        # this needs to be a valid bundle or AppID otherwise it will fail
        # for testing assuming it's valid example: [com.facebook.Facebook]
        args.country = "US"

        #everything above to the func def for testing purposes - define any vars above
        iTunes = iTunesClient(self.sess)
        log.debug("searchTerm: %s" % args.searchTerm )
        appInfos = iTunes.search(term=args.searchTerm)

        if appInfos.resultCount < 1:
            log.fatal("Couldn't find any apps related to the term %s in country %s" % (args.searchTerm, args.country))
            return
        
        options = []
        for i in appInfos.results:
            options.append(i.bundleId)

        title = "Which is the correct app?"
        option, index = pick(options, title, indicator='=>', default_index=0)

        appInfo = appInfos.results[index]
        log.debug("Found app:\n\tName: %s\n\tVersion: %s\n\tbundleId: %s\n\tappId: %s" % (appInfo.trackName, appInfo.version, appInfo.bundleId, appInfo.trackId))
        self.appId = appInfo.trackId
        self.appInfo = appInfo
                
        # I'm not a huge fan of this UX but for now it will work
        user_input = input("Start downloading [ %s ] ? [yes/no] " % option)
        yes_choices = ['yes', 'y']
        no_choices = ['no', 'n']

        if user_input.lower() in yes_choices:
            self.handleDownload(args)
        elif user_input.lower() in no_choices:
            print('user typed no')
        else:
            print('Type yes or no')

        