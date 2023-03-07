#!/usr/bin/env

# handle logging

def get_zipinfo_datetime(timestamp=None):
    # Some applications need reproducible .whl files, but they can't do this without forcing
    # the timestamp of the individual ZipInfo objects. See issue #143.
    timestamp = int(timestamp or time.time())
    return time.gmtime(timestamp)[0:6]


def downloadFile(url, outfile):
    with requests.get(url, stream=True) as r:
        totalLen = int(r.headers.get('Content-Length', '0'))
        downLen = 0
        r.raise_for_status()
        with open(outfile, 'wb') as f:
            lastLen = 0
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
                downLen += len(chunk)
                if totalLen and downLen - lastLen > totalLen * 0.05:
                    logger.info("Download progress: %3.2f%% (%5.1fM /%5.1fM)" % (
                    downLen / totalLen * 100, downLen / 1024 / 1024, totalLen / 1024 / 1024))
                    lastLen = downLen

    return outfile

# define the Store codes.
def storeFront():
    print("Get ID of store based on country code")
    # case AE = "143481"
    # case AG = "143540"
    # case AI = "143538"
    # case AM = "143524"
    # case AO = "143564"
    # case AR = "143505"
    # case AT = "143445"
    # case AU = "143460"
    # case AZ = "143568"
    # case BB = "143541"
    # case BD = "143490"
    # case BE = "143446"
    # case BG = "143526"
    # case BH = "143559"
    # case BM = "143542"
    # case BN = "143560"
    # case BO = "143556"
    # case BR = "143503"
    # case BS = "143539"
    # case BW = "143525"
    # case BY = "143565"
    # case BZ = "143555"
    # case CA = "143455"
    # case CH = "143459"
    # case CI = "143527"
    # case CL = "143483"
    # case CN = "143465"
    # case CO = "143501"
    # case CR = "143495"
    # case CY = "143557"
    # case CZ = "143489"
    # case DE = "143443"
    # case DK = "143458"
    # case DM = "143545"
    # case DO = "143508"
    # case DZ = "143563"
    # case EC = "143509"
    # case EE = "143518"
    # case EG = "143516"
    # case ES = "143454"
    # case FI = "143447"
    # case FR = "143442"
    # case GB = "143444"
    # case GD = "143546"
    # case GH = "143573"
    # case GR = "143448"
    # case GT = "143504"
    # case GY = "143553"
    # case HK = "143463"
    # case HN = "143510"
    # case HR = "143494"
    # case HU = "143482"
    # case ID = "143476"
    # case IE = "143449"
    # case IL = "143491"
    # case IN = "143467"
    # case IS = "143558"
    # case IT = "143450"
    # case JM = "143511"
    # case JO = "143528"
    # case JP = "143462"
    # case KE = "143529"
    # case KN = "143548"
    # case KR = "143466"
    # case KW = "143493"
    # case KY = "143544"
    # case KZ = "143517"
    # case LB = "143497"
    # case LC = "143549"
    # case LI = "143522"
    # case LK = "143486"
    # case LT = "143520"
    # case LU = "143451"
    # case LV = "143519"
    # case MD = "143523"
    # case MG = "143531"
    # case MK = "143530"
    # case ML = "143532"
    # case MO = "143515"
    # case MS = "143547"
    # case MT = "143521"
    # case MU = "143533"
    # case MV = "143488"
    # case MX = "143468"
    # case MY = "143473"
    # case NE = "143534"
    # case NG = "143561"
    # case NI = "143512"
    # case NL = "143452"
    # case NO = "143457"
    # case NP = "143484"
    # case NZ = "143461"
    # case OM = "143562"
    # case PA = "143485"
    # case PE = "143507"
    # case PH = "143474"
    # case PK = "143477"
    # case PL = "143478"
    # case PT = "143453"
    # case PY = "143513"
    # case QA = "143498"
    # case RO = "143487"
    # case RS = "143500"
    # case RU = "143469"
    # case SA = "143479"
    # case SE = "143456"
    # case SG = "143464"
    # case SI = "143499"
    # case SK = "143496"
    # case SN = "143535"
    # case SR = "143554"
    # case SV = "143506"
    # case TC = "143552"
    # case TH = "143475"
    # case TN = "143536"
    # case TR = "143480"
    # case TT = "143551"
    # case TW = "143470"
    # case TZ = "143572"
    # case UA = "143492"
    # case UG = "143537"
    # case US = "143441"
    # case UY = "143514"
    # case UZ = "143566"
    # case VC = "143550"
    # case VE = "143502"
    # case VG = "143543"
    # case VN = "143471"
    # case YE = "143571"
    # case ZA = "143472"

    # init?(countryCode: String) {
    #     guard let value = Storefront.allCases.first(where: { "\($0)" == countryCode }) else {
    #         return nil
    #     }
    #     self = value

