#!/usr/bin/env python3
import json
import math
import sys
import os
import time
from pathlib import Path


### TODO - 
# Clean up the formatting. 
# we should standardize where the parameters are going i.e. (self,device,bundleId/targetdev/whatever)
# I should probably break this up to a more manageable class - 
# - break apps into a objects
# - break devices into individual device objs
# - change everything to be obj oriented instead of always passing - will help with concurrency later

# local imports
from utils import utils
from scrape import downloader

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

# using the https://github.com/doronz88/pymobiledevice3 lib
from pymobiledevice3 import usbmux
# lockdown client handles the majority of communications1
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.diagnostics import DiagnosticsService
from pymobiledevice3.services.installation_proxy import InstallationProxyService
from pymobiledevice3.services.dvt.instruments.device_info import DeviceInfo
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.services.springboard import SpringBoardServicesService
from pymobiledevice3.services.syslog import SyslogService
# these are the developer options which need the device to have a Dev Image mounted first
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
from pymobiledevice3.services.mobile_image_mounter import MobileImageMounterService
from pymobiledevice3.services.os_trace import OsTraceService


DISK_IMAGE_TREE = 'https://api.github.com/repos/pdso/DeveloperDiskImage/git/trees/master'
IMAGE_TYPE = 'Developer'

# input - version of Developer Image to download
# return - bool - did it download successfully? 
def downloadVersion(version):
	dmg_url = 'https://raw.githubusercontent.com/pdso/DeveloperDiskImage/master/{}/DeveloperDiskImage.dmg'.format(version)
	signature = 'https://raw.githubusercontent.com/pdso/DeveloperDiskImage/master/{}/DeveloperDiskImage.dmg.signature'.format(version)
	
	log.debug('Dowloading DeveloperDiskImage.dmg file') # not working...
	log.halt("This hasn't been completed. fixme")


# class Devices will handle multiple devices
class Devices(object):
	# input - self(obj)
	# return - initializes a Devices obj and returns to the calling func
	def __init__(self):
		log.debug("Self Obj Created: [%s]" % self)
		self.devices = self.getDevicesConnected()
	
	# input - self(obj)
	# return - connected_devices(list[Device(obj)]) - list of Device objects
	def getDevicesConnected(self):
		connected_devices = []
		try: 
			lockdown = LockdownClient()
		except:
			log.error("Are you sure a device is connected?")
			sys.exit()

		for device in usbmux.list_devices():
			log.debug("DEVICE: %s" % device)
			udid = device.serial
			lockdown = LockdownClient(udid, autopair=False, usbmux_connection_type=device.connection_type)
			connected_devices.append(lockdown) # adding the entire lockdown obj to the list to return. That way we can pass it
		return connected_devices

	# input - self(obj)
	# return - None - Print device info - ignoring logging here?
	def getDevicesInfo(self):
		log.debug("Devices:")
		for device in self.devices:
			print("\nDevice:[%s]\nIdentifier:[%s]\nVersion:[%s]\n" % (device.display_name, device.identifier, device.product_version))

	# input - self(obj), device_identifier(str) - uses the 'Identifier' string 
	# return - Device(obj) - returns the Lockdown Client Obj for the target device
	def getLockdown(self,device_identifier):
		for device in self.devices:
			if device_identifier == device.short_info['Identifier']:
				log.debug("Found our target device: [%s]" % device_identifier)
				return Device(device)
		log.fatal("Couldn't find target device")

# class Device will handle a single device
class Device(object):
	def __init__(self, target):
		log.debug("Initializing Device Tool Obj")
		self.apps = []
		self.device = target

	# input - self(obj)
	# return - bool - Status of getting all Installed Apps for a device
	def getAllInstalledApps(self):
		log.debug("Finding all Apps Installed on Device [%s]" % self.device)
		all = []
		for device in self.devices:
			self.searchAppDomains(device)

	### get a list of Apps installed based on app_type: ['User', 'System', 'Hidden'] # case sensitive
	# input - 
	# return - 
	def searchAppDomains(self,device):
		search = []
		app_types = ['User', 'System', 'Hidden']
		for app_type in app_types:
			search.append(self.getApps(app_type,device))
		return search # returns a list of dicts

	# input - 
	# return - 
	def getApps(self,app_type,device):
		log.debug("Searching Domain [%s] on Device [%s]" % (app_type,device.short_info['Identifier']))
		return InstallationProxyService(lockdown=device).get_apps(app_type) # this is a return type of dict
	
	# input - lockdown obj
	# return - available device storage in byte_size(str)
	def getDeviceStorage(self):
		return self.device.all_domains['com.apple.disk_usage']['AmountDataAvailable']

	# input - lockdown obj, app (file path)
	# return - bool - Status of installation
	# actually we should take the app obj and not the file path
	# TODO: Handle min OS versioning
	def installApp(self,filepath,bundleId) -> bool:
		log.debug("Installing %s on %s" % (filepath, self.device.short_info['Identifier']) )
		# check for existing apps already
		if self.isAppInstalled(bundleId):
			log.debug("[%s] is already installed on [%s]" % (bundleId,self.device))
			if utils.choice("Would you like to uninstall [%s] first?" % bundleId):
				log.debug("Uninstalling now....")
				self.uninstallApp(bundleId)
				if not self.isAppInstalled(bundleId):
					log.debug("Successfully uninstalled, reinstalling now")
					InstallationProxyService(lockdown=self.device).install_from_local(filepath)
					return True
				else:
					log.error("Failed to uninstall correctly. Please remove the target app manually")
					return False
			else:
				return True
		else:
			log.debug("App is not installed, starting install...")

			InstallationProxyService(lockdown=self.device).install_from_local(filepath)
			if self.isAppInstalled(bundleId):
				log.debug("App successfully installed, launching now")
				return True
			else:
				log.error("Error, try again")
				return False

	# input - self, bundleId (str), device (lockdown obj)
	# return - Bool - was the app successfully uninstalled?
	def uninstallApp(self,bundleId):
		log.halt("fix this...")
		log.debug("Uninstalling %s on %s" % (bundleId, self.device.short_info))
		try:
			InstallationProxyService(lockdown=self.device).uninstall(bundleId)
			return True
		except:
			log.error("Error uninstalling")
			return False

	# input - self, device(Lockdown client object), bundleId (string)
	# return - Bool - Is the application currently installed on the target device?
	def isAppInstalled(self,bundleId):
		# this is slow af. we need to speed this up somehow. 
		# I _doubt_ this will change as frequently as some system resources
		# so maybe some sort of file caching of current system/hidden apps?
		# or async do a search of apps upon initial spin up. but that will require me to learn async
		log.debug("Is %s installed on %s?" % (bundleId,self.device.short_info))
		domains = self.searchAppDomains(self.device)
		# search should be a list of dicts
		for apps in domains:
			# parse the list first
			for app in apps.keys():
				#log.debug("checking %s against %s" % (bundleId.lower(),app.lower()))
				if bundleId.lower() == app.lower():
					log.debug("App is already installed")
					return True
		return False
	
	# input self, app_size(bytes)
	# return - Bool - Will the app fit on the device? 
	def isFull(self,app_size):
		log.halt("isFull() - fixme")
		log.debug("[%s] Storage: " % utils.convert_size(self.getDeviceStorage(device)))
	
	# input - device (lockdown obj)
	# return - bool - does the device have root perms?
	def isRoot(self):
		log.halt("isRoot() - Fixme")
		#ssh to phone whoami over usbmux port forwarder
		# 1. port forward
		# 2. try to ssh
		# 3. run commands (whomai)
		# 4. report status


	# input - device (lockdown client)
	# return - bool - if Frida is installed and running
	def isFridaInstalled(self,device):
		log.halt("isFridaInstalled() - fixme")
	
	# input - device (lockdown obj), bundleId (str)
	# return - bool - return status of app launch
	def launchApp(self,bundleId):
		if self.isMounted():
			with DvtSecureSocketProxyService(lockdown=self.device) as dvt:
				self.pid = ProcessControl(dvt).launch(bundle_id=bundleId)
			log.debug("PID: %s" % self.pid)
			return True
			# self.appRunning(device,bundleId) # TODO we could do some manual verification or even get current foreground app/pid
		else:
			self.mountHandler(self.device)
			# after successfully mounted start over. 

	# input - device (lockdown obj)
	# return - bool - did the app launch successfully?
	def appRunning(self,bundleId):
		log.debug("Is [%s] App Running on device [%s]?" % (bundleId,self.device))
		expression = bundleId
		processes_list = OsTraceService(lockdown=self.device).get_pid_list().get('Payload')
		for pid, process_info in processes_list.items():
			process_name = process_info.get('ProcessName')
			if expression in process_name:
				return True
		return False

	# input - device
	# return - bool - is device mounted or nah?
	def isMounted(self):
		image_mounter = MobileImageMounterService(lockdown=self.device)
		if image_mounter.is_image_mounted(IMAGE_TYPE):
			log.debug("Device is already mounted")
			return True
		else: return False
		
	# input - device (lockdown obj)
	# return - bool - Status of mounting device0
	def mountDevice(self):
		log.debug("Mounting device: [%s]" % self.device)
		image_mounter = MobileImageMounterService(lockdown=self.device)
		# get image_path and sig
		image_path = Path(self.image_path)
		signature = Path(self.sig_path)
		image_path = image_path.read_bytes()
		signature = signature.read_bytes()
		image_mounter.upload_image(IMAGE_TYPE, image_path, signature)
		image_mounter.mount(IMAGE_TYPE, signature)
		log.info('DeveloperDiskImage mounted successfully')

	# input - device (lockdown obj)
	# return - None
	def mountHandler(self):
		# mount
		log.debug('Trying to figure out the best suited DeveloperDiskImage')
		version =  self.device.product_version
		log.debug("iOS Version: %s" % self.device.product_version)
		if self.isVersionAvailable(version):
			log.debug("Version already downloaded locally") # continue with mounting
			self.mountDevice()
		else:
			log.debug("Version not available, need to download") # need to download version
			log.halt("Need to write the downloader")
			# downloadVersion(version)

	# input - version of Developer Image needed for lockdown mounter
	# return - bool - also sets the self.image_path and self.sig_path
	def isVersionAvailable(self,version):
		dev_image = "./downloads/devImages/{}/DeveloperDiskImage.dmg".format(version)
		dev_sig = "./downloads/devImages/{}/DeveloperDiskImage.dmg.signature".format(version)
		if os.path.exists(dev_image) and os.path.exists(dev_sig):
			log.debug("Found: [%s]" % dev_image)
			self.image_path = dev_image
			self.sig_path = dev_sig
			return True
		else:
			log.debug("Not found: [%s] or [%s]" % (dev_image,dev_sig))
			return False