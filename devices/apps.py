#!/usr/bin/env python3
from pymobiledevice3.services.installation_proxy import InstallationProxyService

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

GET_APPS_ADDITIONAL_INFO = {'ReturnAttributes': ['CFBundleIdentifier', 'StaticDiskUsage', 'DynamicDiskUsage']}

class AppManager(object):
    def __init__(self,device):
        self.apps = []
        self.device = device # lockdown obj stored for later use
        self.installed_apps() # get the current apps installed on startup
        log.debug("End of AppManager __init__")

    def add_app(self, app):
        if isinstance(app, App):
            self.apps.append(app)
        else:
            raise ValueError("Invalid object type. Only instances of 'App' class can be added.")
    
    def get_apps(self):
        return self.apps

    def is_installed(self,bundleId):
        for app in self.apps:
             if app.bundleId == bundleId:
                 return True
        return False

    # input - self(obj), bundleId(str)
    # return - get the App Object and return to caller
    def get_app(self,bundleId):
        for app in self.apps:
             if app.bundleId == bundleId:
                return app
        # if we get to here something went wrong
        log.fatal("App not found! Panic!")

    def installed_apps(self):
        log.debug("Retrieving info for all installed apps for device: [%s]" % self.device.identifier)
        results = InstallationProxyService(lockdown=self.device).get_apps()
        for entry in results:
            self.add_app(App(entry))

    def refresh_apps(self):
        log.debug("Refreshing App Info: [%s]" % self.device.identifier)
        results = InstallationProxyService(lockdown=self.device).get_apps()
        self.apps = [] # I think I need to clear this since we are appending? 
        for entry in results:
            self.add_app(App(entry))
        log.debug("Apps Refreshed")

# look into adding kwargs to get extra info
class App(object):
    def __init__(self,app):
        self.name = app.get('CFBundleName')
        self.bundleId = app.get('CFBundleIdentifier')
        self.path = app.get('Path')
        self.min_version = app.get('MinimumOSVersion')
        # add more? 
        log.debug("App Initialization for [%s]" % self.name)
