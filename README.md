# Pumpkin
### Cracking iOS Apps
	# todo - 
	# thread the API server
	# Check devices 
	# auth for a generic account
	# download files
	# try/catch errything for better error handling

### Structure - ./Pumpkin
1. Root Level (You are here.) - pumpkin.py handles running all the necessary services/daemons
2. API Handles - base of the web UI
3. pymobiledevice3 - will be used for collecting info about the ios platform and installing ipa files
4. IPATool Handles downloads
5. frida-ios-dump Handles decrypting apps
6. Web Front end - for ease of use

#### API - backend/api.py
API will allow for the consumption of data that is platform agnostic. No matter what OS you are on, as long as you can make curl/HTTP requests you will be able to get data from the server. 
The API will be custom rolled by me using a common Python API server - prob either Requests API or Django maybe? Might need some MVC for the web UI, but that's down the road in the #Future Research/Work
Design paramaters: All API requests will return JSON data. 
- Todo:

#### API - cli/cmdline.py
Future development - have a cmdline utility that can make and recieve the HTTP requests for the Pumpkin server. 

#### pymobiledevice3 - device/device.py
pymobiledevice3 is based off of pymobiledevice3 on Github https://github.com/doronz88/pymobiledevice3 - the pymd3 project allows Pumpkin communicate with a physical device using the lockdown service that is running on iOS devices. pymd3 will be used to handle all physical device communications including but not limited to, installation of IPA files, execution of decryption commands(tbd), screenshots, device storage checking, etc
- Todo: 
1. Massage the pymd3 into the current project to be callable
2. get device storage
3. before uploading/installing make sure enough storage is available. 
4. installation of media
5. call the decryption functions
6. cleanup - do we need to remove the apps from the phone? 
7. download of decrypted apps
8. send to storage handler

#### IPA Decryption device/decrypt.py
frida-ios-dump is based off of frida-ios-dump on Github https://github.com/AloneMonkey/frida-ios-dump
bfdecrypt - https://github.com/BishopFox/bfdecrypt
- Todo - Things needed for frida-ios-dump

#### IPATool - scrape/scrape.py
IPATool is based off of IPATool-py on Github https://github.com/NyaMisty/ipatool-py
Building information -
Should be callable from all other python scripts in the Pumpkin directory
Should be able to handle 
- Todo - Things needed for IPATool
1. Handle errors in a more graceful way
2. Handle 2fa input
3. Handle environment vars, or stored creds somehow? 
4. Ensure proper structure for calling from within different dirs



#### Corellium Integration - utils/corellium.py
The Corellium portion of this project is attempting to integrate the Pumpkin project with automated deployment with the Corellium API 

#### MobSF Integration - utils/mob.py
The MobSF portion of this project is attempting to integrate the Pumpkin project with the MobSF API for automated analysis

#### Future Research/Work/Requests
1. Automated download of large list of apps from the app store
2. Automated analysis of the apps using the MobSF engine
3. Connecting to a device for debugging purposes
4. Better logging for debugging and web UI inspection