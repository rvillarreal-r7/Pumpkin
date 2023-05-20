#!/usr/bin/env python3
import json
import math
import sys
import asyncio
import time

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter()

# using the https://github.com/doronz88/pymobiledevice3 lib
from pymobiledevice3 import usbmux
# lockdown client handles the majority of communications
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.diagnostics import DiagnosticsService
from pymobiledevice3.services.installation_proxy import InstallationProxyService
from pymobiledevice3.services.dvt.instruments.device_info import DeviceInfo
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.services.springboard import SpringBoardServicesService
from pymobiledevice3.services.syslog import SyslogService

### Define different output based on web request or cmdline
### This is going to get moved into Utils eventually
def print_json(buf):
    formatted_json = json.dumps(buf, sort_keys=True, indent=4)
    log.debug(formatted_json)

# takes byte sizes and will convert to human readable format for printing to screen
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class DeviceTool(object):
	def __init__(self):
		log.debug(self)
		log.debug("Initializing Device Tool Obj")
		# self.devices is a list of all devices individual lockdown object
		self.devices = self.getDevicesConnected()
		self.apps = []

	### Connect to a single device and pass back the Lockdown object
	def getLockdown(self,device_identifier):
		for device in self.devices:
			print(device.short_info['Identifier'])
			if device_identifier == device.short_info['Identifier']:
				print("Found our target device")
				return device
		log.fatal("Couldn't find target device")

	### Connect to multiple devices and pass back a list of Lockdown objs
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

	### get a specific device info
	def getDevicesInfo(self):
		for device in self.devices:
			log.info(DiagnosticsService(lockdown=device).info())

	### get a list of Apps installed based on the user/system workspace
	# I think I could probably prematurely optimize this by splitting it between [n]
	# devices where n is the number of devices discovered.
	def getAllInstalledApps(self):
		log.debug("Finding all Apps Installed")
		# need to split up between user and system space
		app_types = ['User','System','Hidden']
		# for each device we can do at most 1 request per thread
		start = time.perf_counter()
		all = []
		for device in self.devices:
			self.searchAppDomains(device)
		duration = (time.perf_counter() - start)
		log.info("Finished searching all devices in %s seconds" % duration)

	### get a list of Apps installed based on app_type: ['User', 'System', 'Hidden'] # case sensitive
	def searchAppDomains(self,device):
		app_types = ['User', 'System', 'Hidden']
		for app_type in app_types:
			self.apps.append(self.getApps(app_type,device))

	def getApps(self,app_type,device):
		log.debug("[%s][%s]" % (device.short_info['Identifier'],app_type))
		return InstallationProxyService(lockdown=device).get_apps(app_type)
	
	# input - lockdown obj
	# return - available device storage in byte_size(str)
	def getDeviceStorage(self,lockdown):
		return lockdown.all_domains['com.apple.disk_usage']['AmountDataAvailable']

	# input - lockdown obj, app (file path)
	# actually we should take the app obj and not the file path
	def installApp(self,filepath,device):
		log.debug("Installing %s on %s" % (filepath, device.short_info['Identifier']) )
		# check for existing apps already
		#self.isAppInstalled(app)
		log.debug("App: %s" % filepath)
		InstallationProxyService(lockdown=device).install_from_local(filepath)
		log.debug("Success?")

	def uninstallApp(self,bundleId,device):
			log.debug("Uninstalling %s on %s" % (bundleId, device.short_info['Identifier']) )
			# check if app is installed already
			log.debug("App: %s" % bundleId)
			InstallationProxyService(lockdown=device).uninstall(bundleId)
			log.debug("Success? - Check manually for now")

	#
	#
	def isAppInstalled(self,app):
		for device in self.devices:
			print(device)

	#
	#
	def isFull(self,app_size):
		for device in self.devices:
			log.debug("[%s] Storage: " % convert_size(self.getDeviceStorage(device)))

	# input - lockdown obj
	# return list of running processes
	def getProcs(lockdown: LockdownClient):
		""" show process list """
		print_json(OsTraceService(lockdown=lockdown).get_pid_list().get('Payload'))
	
	def isRoot(self,device):
		print("is root?")

	# input - lockdown obj, app obj
	def appExists(lockdown,app):
		log.debug("Checking for %s on %s" % (app, lockdown.short_info))
		print("app exists")
       
#### SPRINGBOARD FUNCS
def getSBState(lockdown):
	log.debug(SpringBoardServicesService(lockdown=lockdown).get_icon_state())

### DEBUGGING FUNCS
def getSysLog(lockdown):
	for line in SyslogService(lockdown=lockdown).watch():
		log.debug(line)

def test():
	devices = getDevicesConnected()
	for device in devices:
		log.debug(device.short_info)