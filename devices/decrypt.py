#!/usr/bin/env python3
import codecs,frida,os,tempfile,shutil

# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)


#globs
TEMP_DIR = tempfile.gettempdir()
PAYLOAD_DIR = 'Payload'
PAYLOAD_PATH = os.path.join(TEMP_DIR, PAYLOAD_DIR)


class FridaSession(object):
    def __init__(self,device):
        log.debug("Initializing FridaSession Obj")
        self.session = self.setupSession(device)
        #self.tmp_dir = self.create_dir()
        #log.halt(self.tmp_dir)

    def setupSession(self,device):
        try:
            return frida.get_device(device.identifier)
        except:
            log.fatal("Error getting FridaSession")

    def dump(self):
        log.debug('dump')

    def create_dir(self):
        log.halt("create dir")
        # path = path.strip()
        # path = path.rstrip('\\')
        # if os.path.exists(path):
        #     print("dear god...")
        #     #shutil.rmtree(path)
        # try:
        #     os.makedirs(path)
        # except os.error as err:
        #     print(err)
    
    def load_js_file(self, session, filename):
        source = ''
        with codecs.open(filename, 'r', 'utf-8') as f:
            source = source + f.read()
        log.halt("huh? fixme")
        script = session.create_script(source)
        script.on('message', on_message)
        script.load()
        return script

    

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