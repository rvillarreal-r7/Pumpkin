#!/usr/bin/env python3
from flask import Flask, render_template, send_file

import sys, time, asyncio
from threading import Thread
# external imports
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.exceptions import PyMobileDevice3Exception
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.base_service import BaseService
from pymobiledevice3.lockdown import LockdownClient
from io import BytesIO
from PIL import Image
import base64

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


app = Flask(__name__)

@app.route('/')
def display_image():
    # Create a BytesIO object to hold the image data
   image_bytes = sc.take_screenshot()
   image_stream = BytesIO()
   image_stream.write(image_bytes)
   image_stream.seek(0)
   return render_template('image.html', image_data=base64.b64encode(image_stream.getvalue()).decode())
   
if __name__ == "__main__":
   try: 
      lockdown = LockdownClient()
      sc = ScreenshotService(lockdown=lockdown)
   except:
      print('error getting lockdown')
      import sys; sys.exit()

   # start the flask server
   app.run(port=8000, debug=True)