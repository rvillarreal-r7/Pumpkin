# Pumpkin
### Cracking iOS Apps

### Structure - Pumpkin dir
1. Root Level (You are here.) - pumpkin.py handles running all the necessary services/daemons
2. API Handles - base of the web UI
3. pymobiledevice3 - will be used for collecting info about the ios platform and installing ipa files
4. IPATool Handles downloads
5. frida-ios-dump Handles decrypting apps
6. Web Front end - for ease of use


#### API - backend dir
The API will be custom rolled by me using a common Python API server - prob either Requests API or Django maybe? Might need some MVC
The API should be callable from a curl request and return properly parsed strings/json/whatever from different tools

#### pymobiledevice3 - device dir
pymobiledevice3 is based off of pymobiledevice3 on Github https://github.com/doronz88/pymobiledevice3
Building information - 
Currently callable only from within the device directory

Todo - Things needed for pymobile3
1. Get device size
2. Fully understand everything allowed from the dylib tcp port

#### IPATool - scrape dir
IPATool is based off of IPATool-py on Github https://github.com/NyaMisty/ipatool-py
Building information -
Should be callable from all other python scripts in the Pumpkin directory
Should be able to handle 

Todo - Things needed for IPATool
1. Handle errors in a more graceful way
2. Handle 2fa input
3. Handle environment vars, or stored creds somehow? 
4. Ensure proper structure for calling from within different dirs


#### frida-ios-dump - decrypt dir
frida-ios-dump is based off of frida-ios-dump on Github https://github.com/AloneMonkey/frida-ios-dump

Todo - Things needed for frida-ios-dump 
1. Do I need to make sure to handle USB and network devices correctly? 


#### Web Front End - backend dir
This will again be custom rolled by me for consumption of the API backend which should already be further along. 
The Front end should be able to handle ease of use UI. 
If we ever want to deploy it as a service then the web front end/api will need to handle sessions and auth


#### Corellium - corel dir
The Corellium portion of this project is attempting to integrate the Pumpkin project with automated deployment with the Corellium API 


#### Future Research/Work
1. Further understanding of the Apple Fairplay decryption process. See if we can consolidate to not using a jailbroken device - the dream :tm:
2. Automated download of large or list of apps from the app store
3. Automated analysis of the apps using the MobSF engine
4. Connecting to a device for debugging purposes