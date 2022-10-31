#!/usr/bin/env
import os
import subprocess
import json

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
    print(formatted_json)


##############################################################
### DEVICE INFO FUNCS ####333
### will print a list of connected devices
def getDevicesConnected():
	connected_devices = []
	lockdown = LockdownClient()
	for device in usbmux.list_devices():
		udid = device.serial
		lockdown = LockdownClient(udid, autopair=False, usbmux_connection_type=device.connection_type)
		connected_devices.append(lockdown.short_info)
	print_json(connected_devices)

### get a specific device info
def getDeviceInfo(lockdown):
	print(DiagnosticsService(lockdown=lockdown).info())

### get a list of Apps installed based on the user/system workspace
def getInstalledApps(lockdown,app_type):
	# need to split up between user and system space
	app_types = []
	print_json(InstallationProxyService(lockdown=lockdown).get_apps(app_type))

def getProcs(lockdown: LockdownClient):
    """ show process list """
    print_json(OsTraceService(lockdown=lockdown).get_pid_list().get('Payload'))


##################################################################
#### SPRINGBOARD FUNCS
####
def getSBState(lockdown):
	print(SpringBoardServicesService(lockdown=lockdown).get_icon_state())


##################################################################
### DEBUGGING FUNCS
###
def getSysLog(lockdown):
	for line in SyslogService(lockdown=lockdown).watch():
		print(line)




###############################
### TEST FUNC ##
##############
def getTest():
	lockdown = LockdownClient()
	#help(LockdownClient) # prints debug info for the LockdownClient Object
	#getInstalledApps(lockdown, "User") # working
	#getInstalledApps(lockdown, "System") # this one is not a JSON serial obj
	getProcs(lockdown) # working
	#getSysLog(lockdown) # working

if __name__ == "__main__":
	getTest()