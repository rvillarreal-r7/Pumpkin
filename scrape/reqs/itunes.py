__all__ = ['iTunesClient']

import json
import re

from scrape.reqs.schemas.itunes_lookup_resp import ItunesLookupResp
import requests

STORE_TABLE = {"AE":"143481-2,32","AG":"143540-2,32","AI":"143538-2,32","AL":"143575-2,32","AM":"143524-2,32","AO":"143564-2,32","AR":"143505-28,32","AT":"143445-4,32","AU":"143460-27,32","AZ":"143568-2,32","BB":"143541-2,32","BE":"143446-2,32","BF":"143578-2,32","BG":"143526-2,32","BH":"143559-2,32","BJ":"143576-2,32","BM":"143542-2,32","BN":"143560-2,32","BO":"143556-28,32","BR":"143503-15,32","BS":"143539-2,32","BT":"143577-2,32","BW":"143525-2,32","BY":"143565-2,32","BZ":"143555-2,32","CA":"143455-6,32","CG":"143582-2,32","CH":"143459-57,32","CL":"143483-28,32","CN":"143465-19,32","CO":"143501-28,32","CR":"143495-28,32","CV":"143580-2,32","CY":"143557-2,32","CZ":"143489-2,32","DE":"143443-4,32","DK":"143458-2,32","DM":"143545-2,32","DO":"143508-28,32","DZ":"143563-2,32","EC":"143509-28,32","EE":"143518-2,32","EG":"143516-2,32","ES":"143454-8,32","FI":"143447-2,32","FJ":"143583-2,32","FM":"143591-2,32","FR":"143442-3,32","GB":"143444-2,32","GD":"143546-2,32","GH":"143573-2,32","GM":"143584-2,32","GR":"143448-2,32","GT":"143504-28,32","GW":"143585-2,32","GY":"143553-2,32","HK":"143463-45,32","HN":"143510-28,32","HR":"143494-2,32","HU":"143482-2,32","ID":"143476-2,32","IE":"143449-2,32","IL":"143491-2,32","IN":"143467-2,32","IS":"143558-2,32","IT":"143450-7,32","JM":"143511-2,32","JO":"143528-2,32","JP":"143462-9,32","KE":"143529-2,32","KG":"143586-2,32","KH":"143579-2,32","KN":"143548-2,32","KR":"143466-13,32","KW":"143493-2,32","KY":"143544-2,32","KZ":"143517-2,32","LA":"143587-2,32","LB":"143497-2,32","LC":"143549-2,32","LK":"143486-2,32","LR":"143588-2,32","LT":"143520-2,32","LU":"143451-2,32","LV":"143519-2,32","MD":"143523-2,32","MG":"143531-2,32","MK":"143530-2,32","ML":"143532-2,32","MN":"143592-2,32","MO":"143515-45,32","MR":"143590-2,32","MS":"143547-2,32","MT":"143521-2,32","MU":"143533-2,32","MW":"143589-2,32","MX":"143468-28,32","MY":"143473-2,32","MZ":"143593-2,32","NA":"143594-2,32","NE":"143534-2,32","NG":"143561-2,32","NI":"143512-28,32","NL":"143452-10,32","NO":"143457-2,32","NP":"143484-2,32","NZ":"143461-27,32","OM":"143562-2,32","PA":"143485-28,32","PE":"143507-28,32","PG":"143597-2,32","PH":"143474-2,32","PK":"143477-2,32","PL":"143478-2,32","PT":"143453-24,32","PW":"143595-2,32","PY":"143513-28,32","QA":"143498-2,32","RO":"143487-2,32","RU":"143469-16,32","SA":"143479-2,32","SB":"143601-2,32","SC":"143599-2,32","SE":"143456-17,32","SG":"143464-19,32","SI":"143499-2,32","SK":"143496-2,32","SL":"143600-2,32","SN":"143535-2,32","SR":"143554-2,32","ST":"143598-2,32","SV":"143506-28,32","SZ":"143602-2,32","TC":"143552-2,32","TD":"143581-2,32","TH":"143475-2,32","TJ":"143603-2,32","TM":"143604-2,32","TN":"143536-2,32","TR":"143480-2,32","TT":"143551-2,32","TW":"143470-18,32","TZ":"143572-2,32","UA":"143492-2,32","UG":"143537-2,32","US":"143441-1,32","UY":"143514-2,32","UZ":"143566-2,32","VC":"143550-2,32","VE":"143502-28,32","VG":"143543-2,32","VN":"143471-2,32","YE":"143571-2,32","ZA":"143472-2,32","ZW":"143605-2,32"}


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