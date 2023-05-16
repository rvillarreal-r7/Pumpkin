#!/usr/bin/env
import json
import requests
import plistlib
import getpass

# fn for testing rate limit and staying within the defined limits
def ratelimit():
   print("being cautious to not overstep my rate limit")


# this is for if you don't have the bundleID
# data = search(term="facebook")
# apps(data)
# different than lookup because we don't have the bundle ID yet. 
def search(term=None, country="US", limit=10, media="software"):
   r = requests.get("https://itunes.apple.com/search?",
                    params={
                        "term": term,
                        "country": country,
                        "limit": limit,
                        "media": media,
                    },
                    headers={
                         "Content-Type": "application/x-www-form-urlencoded",
                    })
   # catch any errors with the responses and make sure it's not null
   try:
      try:
        data = json.loads(r.content)
      except:
        print('Decoding JSON has failed')
      results = int(data["resultCount"])
      if results > 0:
          return data
      else:
          print("No results returned from iTunes")
   except:
       print('Error converting to integer from string value')

# this is for lookups when you know the bundleID
# data = lookup(bundleId="com.Facebook")
# apps(data)
# curl -k -X GET \
    # -H "Content-Type: application/x-www-form-urlencoded" \
    # https://itunes.apple.com/lookup?bundleId=com.touchingapp.potatsolite&limit=1&media=software
def lookup(bundleId=None, appId=None, term=None, country="US", limit=10, media="software"):
   r = requests.get("https://itunes.apple.com/lookup?",
                    params={
                        "bundleId": bundleId,
                        "id": appId,
                        "term": term,
                        "country": country,
                        "limit": limit,
                        "media": media,
                    },
                    headers={
                         "Content-Type": "application/x-www-form-urlencoded",
                    })
   # catch any errors with the responses and make sure it's not null
   try:
      try:
        data = json.loads(r.content)
      except:
        print('Decoding JSON has failed')

      results = int(data["resultCount"])
      if results > 0:
          return data
      else:
          print("No results returned from iTunes")
   except:
       print('Error converting resultCount to integer from string value')

def buyApp(self, appId, appVer='', productType='C', pricingParameters='STDQ'):
  # STDQ - buy, STDRDL - redownload, SWUPD - update
  url = "https://p25-buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct"


   

def downloadApp():
   print("downloading app")

def authenticate():
   # needed constants
   # guid corresponds to macaddress? from the majd/ipatool proj - maybe pull from the iOS device
   guid = "000C2941396B"
   # eventually will need to be removed and implemented in a POST Request from the API/user
   #appleId = input("Username: ")
   appleId = ("ryan_villarreal@rapid7.com")
   password = getpass.getpass()

   # get number of retries
   attempts = 4
   url = "https://p46-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?guid=%s" % guid
   
   # create the dict for the plistlib
   data = dict(appleId=appleId,password=password, attempt=attempts, createSession="true", guid=guid, rmp="0", why="signIn")
   while True:
    print("Sending Auth Request")
    r = requests.post(url, headers={
        "Accept": "*/*", 
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8", 
        },data=plistlib.dumps(data), allow_redirects=False)
    
    ## if the response is a redirect to a new endpoint follow it. 
    if r.status_code == 302:
            print("Redirecting...")
            url = r.headers['Location']
            continue
    
    if r.status_code == 200:
        resp = plistlib.loads(r.content)
        # need logic here to check for 2fa - should return a specific error message if 2fa is enabled. 
        # if you get that error message you should immediately get input from the user to enter the 2fa
        # code and then reauth with the following format: username:password+authCode
        print(json.dumps(resp, indent=1))
        break

def list_apps(data):
    if data != None:
      # handle the entries
      try:
         results = int(data["resultCount"])
      except:
         print('Error converting resultCount to integer from string value')
      for app in data["results"]:
        ## you can extract any and all info here. might be best to just leave it in json format
         print("----------------------------")
         print("App: %s" % (app["trackName"]))
         print("Bundle: %s" % (app["bundleId"]))
         print("Version: %s" % (app["version"]))
         print("\n")
         print(json.dumps(app, indent=1))
         print("\n")

# used for testing - remove before prod
if __name__ == "__main__":
    # this is for testing auth
    authenticate()
    #list_apps(search("Facebook"))