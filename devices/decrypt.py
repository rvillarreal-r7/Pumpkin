#!/usr/bin/env python3
import codecs,frida,os,tempfile,shutil,threading

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

# local imports
from devices import device

#globs
OUTPUT_DIR = tempfile.TemporaryDirectory(dir="./data/output")
PAYLOAD_PATH = os.path.join(OUTPUT_DIR.name + "/Payload")
script_dir = os.path.dirname(os.path.realpath(__file__)) + "/scripts" # script_dir
DUMP_JS = os.path.join(script_dir, 'dump.js') # placeholder for specific script
finished = threading.Event()

def on_message(message, data):
    log.debug("HUH")
    if 'payload' in message:
        payload = message['payload']
        log.debug("PAY")
        if 'dump' in payload:
            log.debug("DUMP")
            origin_path = payload['path']
            dump_path = payload['dump']
    
    print(message)

class FridaSession(object):
    def __init__(self,device):
        log.debug("Initializing FridaSession Obj")
        self.device = device # lockdown obj
        self.devId = device.identifier
        self.session = self.setupSession()

    # input - 
    # return - 
    def setupSession(self):
        try:
            return frida.get_device(self.devId)
        except:
            log.fatal("Error getting FridaSession")

    # input - 
    # return -
    def dump(self,app):
        try:
            self.create_dir() # maybe we make sure the create_dir can't fail instead of doing the other if below.
        except:
            log.fatal('Could not create tmp dir') # panic
       
        if self.tmp_dir == None:
            log.fatal("self.tmp_dir is None") # panic again?
         
        log.debug("Dumping [%s] to [%s]" % (app.bundleId, self.tmp_dir))
        source = self.load_js_file(DUMP_JS)

        # source loaded, now we just need to attach to the current pid
        attached_session = self.session.attach(app.pid)  

        script = attached_session.create_script(source)
        script.on('message', on_message)
        script.load()

        script.post('dump')
        finished.wait()
        log.halt("asdf")
        
    # input - 
    # return -
    def create_dir(self):
        # create temp dir for dumping to
        try:
            os.makedirs(PAYLOAD_PATH)
            self.tmp_dir = PAYLOAD_PATH
        except os.error as err:
            log.halt(err)
    
    # input - self(obj), filename(str/path)
    # return - source(str) - return the dump_js file contents in a string type
    def load_js_file(self, filename):
        log.debug("Reading dump_js from [%s]" % filename)
        source = ''
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                source = source + f.read()
        except:
            log.fatal("Couldn't open script file")
        return source

    
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

