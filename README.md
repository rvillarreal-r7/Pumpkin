# Pumpkin

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
