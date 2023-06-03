#!/usr/bin/env python3
import codecs,frida,os,tempfile,shutil

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)


#globs
OUTPUT_DIR = tempfile.TemporaryDirectory(dir="./data/output")
PAYLOAD_PATH = os.path.join(OUTPUT_DIR.name + "/Payload")
script_dir = os.path.dirname(os.path.realpath(__file__)) + "/scripts" # script_dir
DUMP_JS = os.path.join(script_dir, 'dump.js') # placeholder for specific script

class FridaSession(object):
    def __init__(self,device):
        log.debug("Initializing FridaSession Obj")
        self.session = self.setupSession(device)

    # input - 
    # return - 
    def setupSession(self,device):
        try:
            return frida.get_device(device.identifier)
        except:
            log.fatal("Error getting FridaSession")

    # input - 
    # return -
    def dump(self,app):
        log.debug('Dumping App [%s]' % app.bundleId)
        try:
            self.create_dir()
        except:
            log.fatal('Could not create tmp dir') # panic
       
        if self.tmp_dir == None:
            log.fatal("self.tmp_dir is None") # panic again?
         
        log.debug("Dumping [%s] to [%s]" % (app.bundleId,self.tmp_dir))
        script = self.load_js_file(DUMP_JS)
        
    # input - 
    # return -
    def create_dir(self):
        # create temp dir for dumping to
        try:
            os.makedirs(PAYLOAD_PATH)
            self.tmp_dir = PAYLOAD_PATH
        except os.error as err:
            log.halt(err)
    
    # input - 
    # return - 
    def load_js_file(self, filename):
        source = ''
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                source = source + f.read()
        except:
            log.fatal("Couldn't open script file")
        log.halt("inside load_js_file")
    
    

    def generate_ipa(path, display_name):
        ipa_filename = display_name + '.ipa'

        print('Generating "{}"'.format(ipa_filename))
        try:
            app_name = file_dict['app']

            for key, value in file_dict.items():
                from_dir = os.path.join(path, key)
                to_dir = os.path.join(path, app_name, value)
                if key != 'app':
                    shutil.move(from_dir, to_dir)

            target_dir = './' + PAYLOAD_DIR
            zip_args = ('zip', '-qr', os.path.join(os.getcwd(), ipa_filename), target_dir)
            subprocess.check_call(zip_args, cwd=TEMP_DIR)
            shutil.rmtree(PAYLOAD_PATH)
        except Exception as e:
            print(e)
            finished.set()