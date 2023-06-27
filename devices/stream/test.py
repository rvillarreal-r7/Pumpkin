#!/usr/bin/env python3

# using the https://github.com/doronz88/pymobiledevice3 lib
from pymobiledevice3 import usbmux

from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.exceptions import PyMobileDevice3Exception
from pymobiledevice3.lockdown import LockdownClient
# from pymobiledevice3.services.base_service import BaseService
# from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.service_connection import ServiceConnection

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_session import Session
import uuid


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session(app)
socketio = SocketIO(app, manage_session=True)

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

class Client:
    def __init__(self, uuid):
        self.uuid = uuid

class ClientManager:
    def __init__(self):
        self.clients = {}

    def add_client(self, uuid):
        self.clients[uuid] = Client(uuid)

    def remove_client(self, uuid):
        del self.clients[uuid]

    def list_clients(self):
        print(f'listing {len(self.clients)} clients')
        for client in self.clients:
            print(client)

client_manager = ClientManager()


# webserver|socketio|flask funcs
@app.route('/')
def index():
    return render_template('test.html')

@socketio.on('connect')
def handle_connect(message):
    print(request.sid)
    client_manager.add_client(request.sid)
    
@socketio.on('disconnect')
def handle_disconnect():
    client_manager.remove_client(request.sid)
    print(f"Client {request.sid} disconnected")

@socketio.on('message')
def handle_message(data):
    print(f"Received message from client {request.sid}: {data}")

@socketio.on('refresh')
def handle_message():
    socketio.send()
    print(f"updating clients: {client_manager.list_clients()}")

if __name__ == '__main__': 
    
    
    sc = ScreenshotService(lockdown=lockdown)
    #socketio.run(app, port=8000, debug=True)