#!/usr/bin/env python3
from pymobiledevice3.exceptions import NoDeviceSelectedError
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.services.base_service import BaseService
from pymobiledevice3.exceptions import PyMobileDevice3Exception

from io import BytesIO
from PIL import Image
import base64
import time

class Performance:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.msg = str()
        self.verbose = False
    
    def stop(self):
        self.end_time = time.time()
        return self

    def get_msg(self):
        if self.msg:
            return self.msg()
    
    def measure(self):
        if self.start_time is None or self.end_time is None:
            print("Please call 'stop' before 'measure'")
            return
        self.duration = self.end_time - self.start_time
        if self.msg:
            print(f"{self.msg} - Finished in {self.duration:.10f}/s")
        else:
            print(f"Duration: {self.duration:.10f} seconds")
        return self

    def start(self,msg=None):
        # handle messages first, since we can remove the overhead before start timer
        # this has to be last. 
        start_time = time.time()
        if start_time:
            self.start_time = start_time
            if msg:
                self.msg = msg
                if self.verbose:
                    print(f'{msg} - at {self.start_time}')
            return True
        #else: # handle errs
            
UDID_ENV_VAR = 'PYMOBILEDEVICE3_UDID'

class ScreenshotService(BaseService):
    SERVICE_NAME = 'com.apple.mobile.screenshotr'

    def __init__(self, lockdown: LockdownClient):
        super().__init__(lockdown, self.SERVICE_NAME, is_developer_service=True)

        dl_message_version_exchange = self.service.recv_plist()
        version_major = dl_message_version_exchange[1]
        dl_message_device_ready = self.service.send_recv_plist(
            ['DLMessageVersionExchange', 'DLVersionsOk', version_major])
        if dl_message_device_ready[0] != 'DLMessageDeviceReady':
            raise PyMobileDevice3Exception('Screenshotr didn\'t return ready state')

    def take_screenshot(self) -> bytes:
        self.service.send_plist(['DLMessageProcessMessage', {'MessageType': 'ScreenShotRequest'}])
        response = self.service.recv_plist()

        assert len(response) == 2
        assert response[0] == 'DLMessageProcessMessage'

        if response[1].get('MessageType') == 'ScreenShotReply':
            return response[1]['ScreenShotData']

        raise PyMobileDevice3Exception(f'invalid response: {response}')

class DeviceInfo:
    def __init__(self, lockdown_client: LockdownClient):
        self.lockdown_client = lockdown_client
        self.product_version = self.lockdown_client.product_version
        self.serial = self.lockdown_client.identifier
        self.display_name = self.lockdown_client.display_name

    def __str__(self):
        if self.display_name is None:
            return f'Unknown device, ios version: {self.product_version}, serial: {self.serial}'
        else:
            return f'{self.display_name}, ios version: {self.product_version}, serial: {self.serial}'

def stream(sc):
    perf = Performance()
    while True:
        perf.start()
        image_bytes = sc.take_screenshot()
        image_stream = BytesIO()
        image_stream.write(image_bytes)
        image_stream.seek(0)
        encoded_image = base64.b64encode(image_stream.getvalue()).decode()
        perf.stop().measure()

if __name__ == "__main__":
    try:
        lockdown_client = create_using_usbmux(serial="0e0499a792fcc045297781ded452c664902ebf31")
    except:
        print('err')
        import sys; sys.exit()
    
    sc = ScreenshotService(lockdown=lockdown_client)
    stream(sc)


