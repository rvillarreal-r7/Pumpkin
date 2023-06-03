#!/usr/bin/env

# external imports
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService


def sc():
     # get lockdown
     with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        out.write(Screenshot(dvt).get_screenshot())