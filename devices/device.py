#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# local imports
from utils import utils
from devices import decrypt
from devices import apps

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

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
# these are the developer options which need the device to have a Dev Image mounted first
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
from pymobiledevice3.services.mobile_image_mounter import MobileImageMounterService
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.tcp_forwarder import TcpForwarder

# external imports
import threading,frida

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
		log.debug("DeviceManager Initializing")
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
			log.debug("Adding Device: [%s]" % device)
			udid = device.serial
			lockdown = LockdownClient(udid, autopair=False, usbmux_connection_type=device.connection_type)
			connected_devices.append(lockdown) # adding the entire lockdown obj to the list to return. That way we can pass it
		return connected_devices

	# input - self(obj)
	# return - None - Print connected devices info
	def list(self):
		for device in self.devices:
			self.getLockdown(device.identifier).info()
		
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
		log.debug("Initializing Device [%s] Tool Obj" % (target.identifier))

		# individual target device in this class - holds the lockdown obj
		self.device = target 

		# AppManager class handles interfacing with app functions (install, uninstall, list, etc)
		self.app_manager = apps.AppManager(self.device)
		log.debug("Device [%s] has [%s] apps installed system wide." % (self.device.identifier, len(self.app_manager.apps)))
		
		# each device will need a USBmuxdaemon, SSH connection, and a frida session to be passed around.		
		self.device.usbConn = self.setupUSBconn()
		self.setupSSHconn()

		# TODO err handling here
		#self.device.frida_session = decrypt.FridaSession(self.device)
		
	def info(self):
		log.info(f'Device: {self.device.short_info}')

	# input - lockdown obj
	# return - available device storage in byte_size(str)
	def getDeviceStorage(self):
		return self.device.all_domains['com.apple.disk_usage']['AmountDataAvailable']
	
	# input self, app_size(bytes)
	# return - Bool - Will the app fit on the device? 
	def isFull(self,app_size):
		log.halt("isFull() - fixme")
		log.debug("[%s] Storage: " % utils.convert_size(self.getDeviceStorage(device)))
	
	# input - None
	# return - None
	def backgroundThread(self):
		log.debug("Threading the forwarder until the script is killed")
		self.device.forwarder.start()
		
	# input - self(obj)
	# return - threading.Thread obj
	def setupUSBconn(self) -> threading.Thread:
		# create a usbmux daemonized object that will allow for interaction with the devices over usb ssh
		self.device.src_port = utils.randPort() # get a rand port that's avail
		self.device.dst_port = 22 # 
		log.debug("Starting USBMuxd on src_port: [%s]" %self.device.src_port)
		try:
			self.device.forwarder = TcpForwarder(self.device.src_port, self.device.dst_port, serial=self.device.identifier)
			log.debug("Forwarder started successfully")
		except:
			log.error("Failed to setup USB connection")
		return threading.Thread(target=self.backgroundThread,daemon=True).start()

	# input - self(obj)
	# return - Paramiko SSH session for later use. 
	def setupSSHconn(self):
		import paramiko
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
		# ugh - don't wanna just use hardcoded creds		
		try:
			client.connect(hostname='localhost', port=self.device.src_port, username="root", password="alpine")
			self.device.sshConn = client
			log.debug("SSH Connection Successful")
		except:
			log.fatal("SSH Client Failed to connect")

	# input - device (lockdown obj)
	# return - bool - does the device have root perms?
	def isRoot(self):
		#ssh to phone whoami over usbmux port forwarder
		# 1. port forward
		# port forward should be setup during init. we can check. 
		if self.device.sshConn:
			# sshConn successfully setup
			try:
				stdin, stdout, stderr = self.device.sshConn.exec_command('whoami')
				resp = stdout.read().decode().strip()
			except:
				log.fatal("Error getting response from SSH Client")
		if resp == "root":
			return True
		else:
			return False

	# input - device (lockdown client)
	# return - bool - if Frida is installed and running
	def isFridaReady(self):
		if self.device.sshConn:
			self.device.frida_session = frida.get_device(self.device.identifier)
			log.debug("sshConn is setup correctly")
			if self.device.frida_session:
				return True
		else:
			log.fatal("Error getting response from SSH Client")
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
		
	# input - device (lockdown obj), bundleId (str)
	# return - bool - return status of app launch
	def launchApp(self,bundleId):
		if self.isMounted():
			with DvtSecureSocketProxyService(lockdown=self.device) as dvt:
				self.pid = ProcessControl(dvt).launch(bundle_id=bundleId)
			if self.pid >= 1:
				log.debug("App [%s] launched successfully on PID [%s]" % (bundleId, self.pid))
				# handle decrypt here
				self.decryptApp(bundleId)
			else:
				log.halt("get error from launch") # need to relaunch
				#self.appRunning(device,bundleId) # TODO we could do some manual verification or even get current foreground app/pid
		else:
			self.mountHandler(self.device)
	
	# input - lockdown obj, app (file path)
	# return - bool - Status of installation
	def installApp(self,filepath,bundleId) -> bool:
		log.debug("Installing %s on %s" % (filepath, self.device.short_info['Identifier']) )
		#print(self.app_manager.is_installed(bundleId))
		# check for existing apps already
		if self.app_manager.is_installed(bundleId):
			if self.uninstallApp(bundleId):
				log.debug("Uninstalled Successful")
				pass # continue with reinstall
			else:
				log.halt("Uninstall Failure: Exit")
				return False

		# can I get a progress bar or something here? 
		log.debug("Installation Proxy Service Starting")
		InstallationProxyService(lockdown=self.device).install_from_local(filepath) # thread?
		log.debug("Installation Proxy Service: Completed")
		
		self.app_manager.refresh_apps()
		
		if self.app_manager.is_installed(bundleId):
			return True
		else:
			log.fatal("Error App did not install correctly")

	# input - self, bundleId (str), device (lockdown obj)
	# return - Bool - was the app successfully uninstalled?
	def uninstallApp(self,bundleId) -> bool:
		log.debug("Uninstalling %s on %s" % (bundleId, self.device.identifier))
		try:
			InstallationProxyService(lockdown=self.device).uninstall(bundleId)
			return True
		except:
			log.error("Error uninstalling")
			return False

	# input - 
	# return - 
	def decryptApp(self,bundleId):
		# check for root and frida session
		if self.isRoot() and self.isFridaReady(): #TODO: i'll probably change the isFridaReady to the FridaSession Obj
			log.debug("Device is rooted and Frida is ready begin dump.")
		else:
			log.fatal("Device is not rooted or unable to get Frida port")
		sesh = decrypt.FridaSession(self.device) # lockdown obj
		
		# handle foreground errors
		target_app = sesh.session.get_frontmost_application()
		if not target_app:
			log.debug("Target App not in the foreground, attempting to collect PID by lookup")
			target_pid = sesh.session.get_process(self.app_manager.get_app(bundleId).name).pid
		else:
			target_pid = target_app.pid
		# I think the app needs to hold the new pid for transport
		self.app_manager.get_app(bundleId).set_pid(target_pid)
		sesh.dump(self.app_manager.get_app(bundleId))
		
		log.halt("Finished. Exiting")


