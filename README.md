# Pumpkin

## What is it?
<<<<<<< HEAD
Pumpkin's goal is to make life easier to obtain decrypted iOS IPA files from the Apple App store. Why would we need to do that? Many customers/clients will request a tester to obtain and show proof-of-concepts from the perspective of a real world user. 
=======
Pumpkin's goal is to make life easier to obtain decrypted iOS IPA files from the Apple App store. Why would we need to do that? Many customers/clients will request Rapid7 Pentesting services to obtain and show proof-of-concepts from the perspective of a real world user. 
>>>>>>> 12819fa (Update README.md)

While performing all of these steps individually is completely possible. Pumpkin's purpose is not to replace already exisiting toolsets in the Mobile Pentesting Community Space, but instead seeks to extend those projects and package multiple tools into a single usable project. 

One possible scenario of using Pumpkin over individual scripts would be the potential to automate the process of scraping the Apple App Store with a list of applications based on appId, decrypt them using various devices, perform a transport to third-party tools such as Mobile Security Framework (MobSF). Or maybe you need to resign the decrypted project and want to upload it to Corellium? Just think of the possibilities. 

Projects that have been integeral to the development of Pumpkin and a huge shoutout to the developers on those projects!
### Third-Party Projects
1. [PyMobileDevice3](https://github.com/doronz88/pymobiledevice3)
2. [ipatool-py](https://github.com/NyaMisty/ipatool-py)
3. [Frida Framework](https://github.com/frida)
4. [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump)

## Design Choices
I am using Python for quickness, but a compiled language might be better later on. 

Additionally, I am currently making the assumption there will be two different ways to interact with the Pumpkin tool. It will either be through the cmdline or through an API endpoint. This should give the project a good bit of flexibility for running a headless server that multiple user's can use, and also the ability to run standalone if you have your own jailbroken iOS device. The current stage of development will approach the project from the cmdline and will implement API nonsense later. 

### Cracking iOS Apps
#### todo - 
1. Setup.py needs to be written/error handled
2. Auth for an Apple account with 2fa. Right now you have to just reauth the second time with the password + token
3. Bug fixes
4. Better device management and setup. 
	a. Devices generally connect fine, but I need to figure out if there is a way to hold the devices in a connected state at all times. 
	b. Load balancing is not right yet. 
5. General work to the API before letting user's interact that way. primary focus is on cmdline for the time being

### Structure - ./Pumpkin
1. Root Level - pumpkin.py handles running all the necessary services/daemons
	a. ./api - Handles base of the web UI/API interactions
	b. ./cli - Handles base of the cli interactions
	c. ./data - Output for 
	3. pymobiledevice3 - will be used for collecting info about the ios platform and installing ipa files
	4. IPATool Handles downloads
	5. frida-ios-dump Handles decrypting apps
	6. Web Front end - for ease of use

### Setup/Installation 
Currently you have to install manually, but don't fret. `python3 setup.py` is coming soon!

Pumpkin was developed using pyenv and the `Python 3.11.2` version. 
