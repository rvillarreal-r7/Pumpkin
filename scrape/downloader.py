#!/usr/bin/python3

# external imports
import sys, plistlib, os, requests, getpass, zipfile
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# local imports
from scrape.reqs.store import *
from scrape.reqs.itunes import *
from utils import utils
from devices import device

# prepend all modules
from utils import utils, logger
log = logger.LogAdapter(__name__)

# globals
DOWNLOAD_DIR = "./data/apps/"

class IPATool(object):
    # input - self(obj)
    # return - None - calling func will have object 
    def __init__(self, args):
        log.debug("Initializing IPATool Obj")
        self.sess = requests.Session()

        # needed self.vars
        self.args = args # attaching the argparse obj to the IPATool for now
        self.appId = None
        self.appVerId = None
        self.appleid = None
        self.applepass = None

        # we will define devices here for load balancing
        # for now we will choose a single device for testing
        # handle if the user wants to choose a device
        self.devices = device.Devices()
        self.target = self.devices.getLockdown("0e0499a792fcc045297781ded452c664902ebf31")

        # self.app_manager = self.target.app_manager()

        # Store session setup
        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    # input - self(obj), _e(str?)
    # return - None 
    def _handleStoreException(self, _e):
        e = _e # type: StoreException
        log.fatal("Store %s failed! Message: %s%s" % (e.req, e.errMsg, " (errorType %s)" % e.errType if e.errType else ''))
        log.fatal("Raw Response: %s" % (e.resp.as_dict()))

    # input - self(obj), args(argparse obj)
    # return - Store(StoreClient obj)
    def _get_StoreClient(self):
        Store = StoreClient(self.sess)

        try:
            if self.args.appleid and self.args.password:   
                self.appleid = self.args.appleid
                self.applepass = self.args.password
            else:
                log.halt(self.appleid) # shouldn't see this for the time being.
        except:
            self.appleid = input("Username: ")
            self.applepass = getpass.getpass()

        log.debug("Logging into iTunes...")
        Store.authenticate(self.appleid, self.applepass)
        log.info('Logged in as %s' % Store.accountName)
        return Store

    # input - self(obj)
    # return - bool - Status if the app is on the local disk [ Not to be confused with isAppInstalled() which checks for the target device]
    def appDownloaded(self) -> bool:
        #
        if self.appInfo.filepath is None:
            f = self.getFilename(self.appInfo.bundleId, self.appInfo.version)
        else:
            f = self.appInfo.filepath
        
        self.appInfo.filepath = DOWNLOAD_DIR + f # reasons
        # before taking auth make sure the app isn't already downloaded to the system
        if os.path.exists(self.appInfo.filepath):
            log.debug("App [%s] is downloaded already" % (self.appInfo.filepath))
            return True
        else:
            log.debug("App [%s] is not downloaded already" % (f))
            return False

    # input - self(obj)
    # return - None
    def handleSearch(self):
        # TODO this needs to be a valid bundle or AppID otherwise it will fail
        self.args.country = "US" # default for now

        # create iTunesClient obj
        iTunes = iTunesClient(self.sess)
        log.debug("searchTerm: %s" % self.args.searchTerm )
        self.appInfos = iTunes.search(term=self.args.searchTerm)

        # if appInfos is < 1 that means we didn't find any apps related to the search. 
        if self.appInfos.resultCount < 1:
            log.fatal("Couldn't find any apps related to the term %s in country %s" % (self.args.searchTerm, self.args.country)) # will panic exit on fatal
        
        # iterate through the results and append the bundleId to an options(list)
        options = []
        for i in self.appInfos.results:
            options.append(i.bundleId)
        options,index = utils.chooseApp(options) # prompt the user for which app they want

        # use the index from the pick utility to set the self.appInfo to specific selection
        # TODO - move the individual app results to it's own Struct
        self.appInfo = self.appInfos.results[index]
        self.appInfo.filepath = self.getFilename(self.appInfo.bundleId, self.appInfo.version)
        log.debug("Found app:\n\tName: %s\n\tVersion: %s\n\tbundleId: %s\n\tappId: %s" % (self.appInfo.trackName, self.appInfo.version, self.appInfo.bundleId, self.appInfo.trackId))

        if self.appDownloaded():
            if self.target.app_manager.is_installed(self.appInfo.bundleId):
                log.halt("here")
                if utils.choice("Would you like to Reinstall [%s]" % (self.appInfo.bundleId)):
                     self.handleInstall()
                else:
                    self.target.launchApp(self.appInfo.bundleId)
            else:
                if utils.choice("App [%s] already downloaded. Would you like to install" % self.appInfo.bundleId):
                    self.handleInstall() # app downloaded but not installed, prompt for install?
        else:
            if utils.choice("Would you like to download [%s]" % self.appInfo.bundleId):
                if self.handleDownload():
                    self.handleInstall()
                else:
                    log.halt("here")
                    self.target = self.getDevice()
                    self.target.launchApp()
            
    # input - self(obj),args(argparse obj)
    # return - bool - Status of lookup
    def handleLookup(self) -> bool:
        # this needs to be a valid bundle or AppID otherwise it will fail - need some error handling here
        log.debug("User Provided BundleID/AppID: %s" % self.args.lookupTerm)
        self.country = "US" # TODO add country modification later
        self.bundle_id = self.args.lookupTerm
        self.appId = None

        if self.bundle_id:
            s = 'BundleID: %s' % self.bundle_id
        else:
            s = 'AppID: %s' % self.appInfo.trackId
        log.info('Looking up app in country "%s" with %s' % (self.country, s))
        iTunes = iTunesClient(self.sess)

        appInfos = iTunes.lookup(bundleId=self.bundle_id, appId=self.appId, country=self.country)
        
        if appInfos.resultCount != 1:
            log.fatal("Failed to find app in country %s with %s" % (self.country, s))
            return False
        
        self.appInfo = appInfos.results[0]
        self.appInfo.filepath = self.getFilename(self.appInfo.bundleId, self.appInfo.version)
        log.debug("Found app:\n\tName: %s\n\tVersion: %s\n\tbundleId: %s\n\tappId: %s" % (self.appInfo.trackName, self.appInfo.version, self.appInfo.bundleId, self.appInfo.trackId))

        if self.appDownloaded():
            if self.target.app_manager.is_installed(self.appInfo.bundleId): 
                if utils.choice("Would you like to Reinstall [%s]" % (self.appInfo.bundleId)):
                    self.handleInstall()
                else:
                    self.target.launchApp(self.appInfo.bundleId)
            else:
                if utils.choice("App [%s] already downloaded. Would you like to install" % self.appInfo.bundleId):
                    self.handleInstall() # app downloaded but not installed, prompt for install?
        else:
            if utils.choice("Would you like to download [%s]" % self.appInfo.bundleId):
                if self.handleDownload():
                    self.handleInstall()
                else:
                    utils.kbye(__name__)

    # input - self,args
    # return - bool - Status of IPA download
    def handleDownload(self) -> bool:
        if not self.appInfo.bundleId and self.appInfo.version:
            log.fatal("AppInfo is empty for some reason... %s" % self.appInfo)
            return False # shouldn't need this but just-n-case

        # try to auth to the app store using the IPATool
        try:
            log.debug("Attempting Apple Store Auth..")
            Store = self._get_StoreClient()
            try:
                Store.purchase(self.appInfo.trackId)
            except StoreException as e:
                if e.errMsg == 'purchased_before':
                    log.warning("You have already purchased appId [%s] before, continuing." % (self.appInfo.bundleId))
            log.info("Retriving download info for appId [%s] with versionId [%s]" % (self.appInfo.bundleId, self.appInfo.version))

            try:
                downResp = Store.download(appId=self.appInfo.trackId)
            except StoreException as e:
                log.fatal("Error: [%s]" % e.errMsg)

            if not downResp.songList:
                log.fatal("Failed to get app download info!")
                raise StoreException('download', downResp, 'no songList')
            downInfo = downResp.songList[0]

            log.info("Downloading IPA to [%s]" % self.appInfo.filepath)
            data = utils.downloadFile(downInfo.URL, self.appInfo.filepath)
            with zipfile.ZipFile(data, 'a') as ipaFile:
                log.info("Writing out iTunesMetadata.plist...")
                metadata = downInfo.metadata.as_dict()
                if self.appleid:
                    metadata["apple-id"] = self.appleid
                    metadata["userName"] = self.appleid
                ipaFile.writestr(zipfile.ZipInfo("iTunesMetadata.plist", utils.get_zipinfo_datetime()), plistlib.dumps(metadata))

                appContentDir = [c for c in ipaFile.namelist() if c.startswith('Payload/') and len(c.strip('/').split('/')) == 2][0]
                appContentDir = appContentDir.rstrip('/')

                scManifestData = ipaFile.read(appContentDir + '/SC_Info/Manifest.plist')
                scManifest = plistlib.loads(scManifestData)

                sinfs = {c.id: c.sinf for c in downInfo.sinfs}
                for i, sinfPath in enumerate(scManifest['SinfPaths']):
                    ipaFile.writestr(appContentDir + '/' + sinfPath, sinfs[i])
            log.info("Completed Download of IPA to %s" % self.appInfo.filepath)
            return True # return Status
        ##############################    
        except StoreException as e:
            self._handleStoreException(e)
 
    # input - self(obj)
    # return - None - maybe status eventually?
    def handleInstall(self):
        target = self.getDevice() # for now no args needed to pass - eventually DeviceID

        # error checking for target
        if target is None:
            log.error("Why is target None?")
            log.halt("fixme")
        
        if self.appInfo.filepath:
            log.debug("Sending [%s] info to Install location" % (self.appInfo.filepath))
            status = target.installApp(self.appInfo.filepath,self.appInfo.bundleId)
        else:
            log.debug("[%s] is already installed just launch" % self.appInfo.bundleId)
            status = True
        
        # if the app is properly installed time to launch
        if status:
            log.debug("Launching [%s] on device [%s] now." % (self.appInfo.bundleId, target))
            if target.launchApp(self.appInfo.bundleId):
                log.halt("Decrypt time!")
            else:
                log.halt("Handle Launch errors")

    # input - self(obj)
    # return - Lockdown Obj - this will eventually become the adapter for the load balancer
    def getDevice(self):
        devs = device.Devices()
        #need a load balancer method, but not a priority for now we will just select one dev
        return devs.getLockdown("0e0499a792fcc045297781ded452c664902ebf31") # remove when loadbalancer

    # input - 
    # return - 
    def getFilename(self,bundleId,ver):
        return '%s-%s.ipa' % (bundleId,ver)