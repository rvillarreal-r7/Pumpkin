#!/usr/bin/python3
import json
import os
import sys
import time
import zipfile
import plistlib
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import requests

from itunes_lookup_resp import ItunesLookupResp
from store_authenticate_req import StoreAuthenticateReq
from store_authenticate_resp import StoreAuthenticateResp
from store_buyproduct_req import StoreBuyproductReq
from store_buyproduct_resp import StoreBuyproductResp
from store_download_req import StoreDownloadReq
from store_download_resp import StoreDownloadResp

### Current Status - 
# Can search for apps based on a term
# Can lookup a specific app using a Bundle ID
#
###

### Todo - 
# Grab a ticket and go
# 1. Handle Auth
# 2. Download files
# 3. Handle 2FA
# 4. Handle versions
# 5. so much cleaning
###

STORE_TABLE = {"AE":"143481-2,32","AG":"143540-2,32","AI":"143538-2,32","AL":"143575-2,32","AM":"143524-2,32","AO":"143564-2,32","AR":"143505-28,32","AT":"143445-4,32","AU":"143460-27,32","AZ":"143568-2,32","BB":"143541-2,32","BE":"143446-2,32","BF":"143578-2,32","BG":"143526-2,32","BH":"143559-2,32","BJ":"143576-2,32","BM":"143542-2,32","BN":"143560-2,32","BO":"143556-28,32","BR":"143503-15,32","BS":"143539-2,32","BT":"143577-2,32","BW":"143525-2,32","BY":"143565-2,32","BZ":"143555-2,32","CA":"143455-6,32","CG":"143582-2,32","CH":"143459-57,32","CL":"143483-28,32","CN":"143465-19,32","CO":"143501-28,32","CR":"143495-28,32","CV":"143580-2,32","CY":"143557-2,32","CZ":"143489-2,32","DE":"143443-4,32","DK":"143458-2,32","DM":"143545-2,32","DO":"143508-28,32","DZ":"143563-2,32","EC":"143509-28,32","EE":"143518-2,32","EG":"143516-2,32","ES":"143454-8,32","FI":"143447-2,32","FJ":"143583-2,32","FM":"143591-2,32","FR":"143442-3,32","GB":"143444-2,32","GD":"143546-2,32","GH":"143573-2,32","GM":"143584-2,32","GR":"143448-2,32","GT":"143504-28,32","GW":"143585-2,32","GY":"143553-2,32","HK":"143463-45,32","HN":"143510-28,32","HR":"143494-2,32","HU":"143482-2,32","ID":"143476-2,32","IE":"143449-2,32","IL":"143491-2,32","IN":"143467-2,32","IS":"143558-2,32","IT":"143450-7,32","JM":"143511-2,32","JO":"143528-2,32","JP":"143462-9,32","KE":"143529-2,32","KG":"143586-2,32","KH":"143579-2,32","KN":"143548-2,32","KR":"143466-13,32","KW":"143493-2,32","KY":"143544-2,32","KZ":"143517-2,32","LA":"143587-2,32","LB":"143497-2,32","LC":"143549-2,32","LK":"143486-2,32","LR":"143588-2,32","LT":"143520-2,32","LU":"143451-2,32","LV":"143519-2,32","MD":"143523-2,32","MG":"143531-2,32","MK":"143530-2,32","ML":"143532-2,32","MN":"143592-2,32","MO":"143515-45,32","MR":"143590-2,32","MS":"143547-2,32","MT":"143521-2,32","MU":"143533-2,32","MW":"143589-2,32","MX":"143468-28,32","MY":"143473-2,32","MZ":"143593-2,32","NA":"143594-2,32","NE":"143534-2,32","NG":"143561-2,32","NI":"143512-28,32","NL":"143452-10,32","NO":"143457-2,32","NP":"143484-2,32","NZ":"143461-27,32","OM":"143562-2,32","PA":"143485-28,32","PE":"143507-28,32","PG":"143597-2,32","PH":"143474-2,32","PK":"143477-2,32","PL":"143478-2,32","PT":"143453-24,32","PW":"143595-2,32","PY":"143513-28,32","QA":"143498-2,32","RO":"143487-2,32","RU":"143469-16,32","SA":"143479-2,32","SB":"143601-2,32","SC":"143599-2,32","SE":"143456-17,32","SG":"143464-19,32","SI":"143499-2,32","SK":"143496-2,32","SL":"143600-2,32","SN":"143535-2,32","SR":"143554-2,32","ST":"143598-2,32","SV":"143506-28,32","SZ":"143602-2,32","TC":"143552-2,32","TD":"143581-2,32","TH":"143475-2,32","TJ":"143603-2,32","TM":"143604-2,32","TN":"143536-2,32","TR":"143480-2,32","TT":"143551-2,32","TW":"143470-18,32","TZ":"143572-2,32","UA":"143492-2,32","UG":"143537-2,32","US":"143441-1,32","UY":"143514-2,32","UZ":"143566-2,32","VC":"143550-2,32","VE":"143502-28,32","VG":"143543-2,32","VN":"143471-2,32","YE":"143571-2,32","ZA":"143472-2,32","ZW":"143605-2,32"}

# class for the ScrapeTool - should allow for portability across the Pumpkin project
# the glue if you will
class ScrapeTool(object):
    def __init__(self):
        self.sess = requests.Session()

        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.appId = None
        # self.appInfo = None
        self.appVerId = None
        self.jsonOut = None

    ## I think this will be our jumping off point for connecting the iTunesClient with the ScrapeTool
    # calling the handleLookup func from the scraper object
    # action can be "search" or "lookup"
    # scraper = ScrapeTool() # build the object
    # bundID = "nexttech" # for search action - doesn't need to be perfect
    # bundID = "com.NexTech.iNexTech" # for lookup action - needs to be valid bundle
    # scraper.handleLookup('lookup',bundID) # calling the func - eventually the action will be used only by the API
    def handle(self,action,bundID):
        if action is not None:
            if action == "search":
                iTunes = iTunesClient(self.sess)
                appInfos = iTunes.search(term=bundID)
                if appInfos.resultCount < 1:
                    print("Failed")
                    return
                for app in appInfos.results:
                    print (app.bundleId,app.trackId)
            elif action == "lookup":
                iTunes = iTunesClient(self.sess)
                appInfos = iTunes.lookup(bundleId=bundID)
                if appInfos.resultCount < 1:
                    print("Failed")
                    return
                for app in appInfos.results:
                    print (app.bundleId,app.trackId)
            else:
                print("action not recongnized")


# class for holding the iTunesClient funcs
class iTunesClient(object):
    def __init__(self, sess: requests.Session):
        self.sess = sess

    # curl -k -X GET \
    # -H "Content-Type: application/x-www-form-urlencoded" \
    # https://itunes.apple.com/lookup?bundleId=com.touchingapp.potatsolite&limit=1&media=software
    def lookup(self, bundleId=None, appId=None, term=None, country="US", limit=1, media="software") -> ItunesLookupResp:
        r = self.sess.get("https://itunes.apple.com/lookup?",
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
        return ItunesLookupResp.from_dict(r.json())


    def search(self, bundleId=None, appId=None,term=None, country="US", limit=10, media="software") -> ItunesLookupResp:
        r = self.sess.get("https://itunes.apple.com/search?",
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
        return ItunesLookupResp.from_dict(r.json())

    def getAppVerId(self, appId, country):
        if not ',' in country:
            storeFront = STORE_TABLE[country.upper()]
        else:
            storeFront = country
        appInfo = requests.get("https://apps.apple.com/app/id%s" % appId, headers={"X-Apple-Store-Front": storeFront}).text
        try:
            appParam = re.findall(r'"buyParams":"(.*?)"', appInfo)[0]
        except:
            appParam = re.findall(r'buy-params="(.*?)"', appInfo)[0]
            appParam = appParam.replace('&amp;', '&')
        appParamDict = dict((c.split('=') for c in json.loads('"%s"' % appParam).split('&')))
        appVer = appParamDict['appExtVrsId']
        return appVer

class StoreException(Exception):
    def __init__(self, req, resp, errMsg, errType=None):
        self.req = req
        self.resp = resp # type: StoreDownloadResp
        self.errMsg = errMsg
        self.errType = errType
        super().__init__(
            "Store %s error: %s" % (self.req, self.errMsg) if not self.errType else
            "Store %s error: %s, errorType: %s" % (self.req, self.errMsg, self.errType))

class StoreClient(object):
    def __init__(self, sess: requests.Session, guid: str = '000C2941396B'):
        self.sess = sess
        self.guid = guid
        self.accountName = None
        self.iTunes_provider = None

    def authenticate(self, appleId, password):
        print("Authenticating...")
        req = StoreAuthenticateReq(appleId=appleId, password=password, attempt='4', createSession="true", guid=self.guid, rmp='0', why='signIn')
        url = "https://p46-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?guid=%s" % self.guid
        while True:
            r = self.sess.post(url,
                      headers={
                          "Accept": "*/*",
                          "Content-Type": "application/x-www-form-urlencoded",
                          "User-Agent": "Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8",
                      }, data=plistlib.dumps(req.as_dict()), allow_redirects=False)
            if r.status_code == 302:
                url = r.headers['Location']
                continue
            break

        resp = StoreAuthenticateResp.from_dict(plistlib.loads(r.content))

        # we need to handle 2fa here. 
        # input('2FA Code: ')
        if not resp.m_allowed:
            ## I figured out the 2FA shit here.... it's so dumb. 
            ## You can basically auth. Then you should be able to grep through the plistlib for an error message
            ## If you "allow" the device from a trusted source it will spit out a 2FA code
            ## just re-run the script and append the 2FA to the end of the password. 
            ## so you could literally do a loop to check to see if that one specific error message exists and if it does then ask user for 2fa code
            ## after 2fa code entered just resend the POST request with the user's password appending the 2fa and ggezpz
            raise StoreException("authenticate", resp.customerMessage, resp.failureType)

        self.sess.headers['X-Dsid'] = self.sess.headers['iCloud-Dsid'] = str(resp.download_queue_info.dsid)
        self.sess.headers['X-Apple-Store-Front'] = r.headers.get('x-set-apple-store-front')
        self.sess.headers['X-Token'] = resp.passwordToken
        self.accountName = resp.accountInfo.address.firstName + " " + resp.accountInfo.address.lastName
        return resp

    # ==> 🛠   
    # [Verbose] Performing request: 
    # curl -k -X POST \
    # -H "iCloud-DSID: 12263680861" \
    # -H "Content-Type: application/x-www-form-urlencoded" \
    # -H "User-Agent: Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8" \
    # -H "X-Dsid: 12263680861" \
    # -d '<?xml version="1.0" encoding="UTF-8"?>
    # <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    # <plist version="1.0">
    # <dict>
    #         <key>creditDisplay</key>
    #         <string></string>
    #         <key>guid</key>
    #         <string>000C2941396B</string>
    #         <key>salableAdamId</key>
    #         <string>1239860606</string>
    # </dict>
    # </plist>
    # ' \
    # https://p25-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct?guid=000C2941396Bk
    def volumeStoreDownloadProduct(self, appId, appVerId=""):
        req = StoreDownloadReq(creditDisplay="", guid=self.guid, salableAdamId=appId, appExtVrsId=appVerId)
        r = self.sess.post("https://p25-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct",
                           params={
                               "guid": self.guid
                           },
                           headers={
                               "Content-Type": "application/x-www-form-urlencoded",
                               "User-Agent": "Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8",
                           }, data=plistlib.dumps(req.as_dict()))

        resp = StoreDownloadResp.from_dict(plistlib.loads(r.content))
        if resp.cancel_purchase_batch:
            raise StoreException("volumeStoreDownloadProduct", resp, resp.customerMessage, resp.failureType + '-' + resp.metrics.dialogId)
        return resp

    def buyProduct(self, appId, appVer='', productType='C', pricingParameters='STDQ'):
        # STDQ - buy, STDRDL - redownload, SWUPD - update
        url = "https://p25-buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct"
        
        itunes_internal = self.iTunes_provider(url)
        hdrs = itunes_internal.pop('headers')
        guid = itunes_internal.pop('guid')
        kbsync = itunes_internal.pop('kbsync')

        if not appVer:
            from reqs.itunes import iTunesClient
            iTunes = iTunesClient(self.sess)
            appVer = iTunes.getAppVerId(appId, hdrs['X-Apple-Store-Front'])

        req = StoreBuyproductReq(
            guid=guid,
            salableAdamId=str(appId),
            appExtVrsId=str(appVer) if appVer else None,
            
            price='0',
            productType=productType,
            pricingParameters=pricingParameters,
            
            # ageCheck='true',
            # hasBeenAuthedForBuy='true',
            # isInApp='false',
        )
        payload = req.as_dict()
        # kbsync is bytes, but json schema does not support it, so we have to assign it
        payload['kbsync'] = kbsync

        hdrs = dict(hdrs)
        hdrs["Content-Type"] = "application/x-apple-plist"

        r = self.sess.post(url,
                        headers=hdrs, 
                        data=plistlib.dumps(payload)
                        )

        resp = StoreBuyproductResp.from_dict(plistlib.loads(r.content))
        if resp.cancel_purchase_batch:
            raise StoreException("buyProduct", resp, resp.customerMessage, resp.failureType + '-' + resp.metrics.dialogId)
        return resp

    def buyProduct_purchase(self, appId, productType='C'):
        url = "https://buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct"
        req = StoreBuyproductReq(
            guid=self.guid,
            salableAdamId=str(appId),
            appExtVrsId='0',

            price='0',
            productType=productType,
            pricingParameters='STDQ',

            hasAskedToFulfillPreorder='true',
            buyWithoutAuthorization='true',
            hasDoneAgeCheck='true',
        )
        payload = req.as_dict()

        r = self.sess.post(url,
                           headers={
                               "Content-Type": "application/x-apple-plist",
                               "User-Agent": "Configurator/2.15 (Macintosh; OS X 11.0.0; 16G29) AppleWebKit/2603.3.8",
                           },
                           data=plistlib.dumps(payload))

        if r.status_code == 500:
            raise StoreException("buyProduct_purchase", None, 'purchased_before')

        resp = StoreBuyproductResp.from_dict(plistlib.loads(r.content))
        if resp.status != 0 or resp.jingleDocType != 'purchaseSuccess':
            raise StoreException("buyProduct_purchase", resp, resp.customerMessage,
                                 resp.status + '-' + resp.jingleDocType)
        return resp

    def purchase(self, appId):
        if self.iTunes_provider:
            return None # iTunes mode will automatically purchase the app if not purchased
        else:
            return self.buyProduct_purchase(appId)

    def download(self, appId, appVer=''):
        if self.iTunes_provider:
            return self.buyProduct(appId, appVer)
        else:
            return self.volumeStoreDownloadProduct(appId, appVer)


if __name__ == "__main__":
    # creating the ScrapeTool object
    Scraper = ScrapeTool()
    Store = StoreClient(Scraper.sess) # need to pass in scraper.sess obj
    #print(Scraper.sess)

    ## Test funcs for getting creds on the cmdline
    from getpass import getpass
    from getpass import getuser
    #appleid = input('Email: ')
    appleid = 'ryan_villarreal@rapid7.com'
    applepass = getpass('Password: ')

    # this works... sorta see notes above about 2fa
    Store.authenticate(appleid,applepass)
    print("Hello, " + Store.accountName)

    # let's try searching for an app now
    Scraper
    Scraper.search(keyword)

