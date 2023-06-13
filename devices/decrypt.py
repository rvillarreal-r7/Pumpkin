#!/usr/bin/env python3
import codecs,frida,os,tempfile,shutil,threading,subprocess
from scp import SCPClient


# prepend all scripts with logger object retrieval
from utils import logger
log = logger.LogAdapter(__name__)

# local imports
from devices import device

#globs
OUTPUT_DIR = tempfile.TemporaryDirectory(dir="./data/output")
PAYLOAD_PATH = os.path.join(OUTPUT_DIR.name + "/Payload/")
script_dir = os.path.dirname(os.path.realpath(__file__)) + "/scripts" # script_dir
DUMP_JS = os.path.join(script_dir, 'dump.js') # placeholder for specific script
finished = threading.Event()
file_dict = {}

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
    def get_file(self,remote_file,category):
        if category == "dump":
            filename = os.path.basename(remote_file)
            output = PAYLOAD_PATH + filename
            log.debug("Get device file: [%s] to local [%s]" % (remote_file, output))
            #log.stack(self.device.sshConn)
            with SCPClient(self.device.sshConn.get_transport(),socket_timeout = 60) as scp:
                scp.get(remote_file,output)
            log.debug("File [%s] downloaded locally, modifying perms" % (filename))
            # we need to chmod the local file I guess?
            chmod_dir = ('chmod', '655', output)
            try:
                subprocess.check_call(chmod_dir)
            except subprocess.CalledProcessError as err:
                    log.error(err)
            log.debug("File [%s] downloaded, and saved locally successfully" % (filename))

        elif category == "app":
            filename = os.path.basename(remote_file)
            output = PAYLOAD_PATH + filename
            log.debug("Get device file: [%s] to local [%s]" % (remote_file, output))
            #log.stack(self.device.sshConn)
            with SCPClient(self.device.sshConn.get_transport(),socket_timeout = 60) as scp:
                scp.get(remote_file,output,recursive=True)
            log.debug("File [%s] downloaded locally, modifying perms" % (filename))
            # we need to chmod the local file I guess?
            chmod_dir = ('chmod', '755', output)
            try:
                subprocess.check_call(chmod_dir)
            except subprocess.CalledProcessError as err:
                    log.error(err)
            log.debug("File [%s] downloaded, and saved locally successfully" % (filename))
            file_dict['app'] = os.path.basename(filename)

        else:
            log.fatal("error")
    
    # input - 
    # return - 
    def on_message(self, message, data):
        log.debug("Message from Frida's on_message")
        if 'payload' in message:
            payload = message['payload']
            if 'dump' in payload:
                origin_path = payload['path']
                dump_path = payload['dump']

                scp_from = dump_path
                self.get_file(scp_from,"dump")

                index = origin_path.find('.app/')
                file_dict[os.path.basename(dump_path)] = origin_path[index + 5:]

            if 'app' in payload:
                app_path = payload['app']
                scp_from = app_path
                self.get_file(scp_from,"app")

            if 'done' in payload:
                finished.set()

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
        script.on('message', self.on_message)
        script.load()

        script.post('dump')
        finished.wait()
        log.debug("Finished with Dump")
        self.generate_ipa(PAYLOAD_PATH, app.name)

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

    # input - 
    # return - 
    def generate_ipa(self, path, display_name):
        ipa_filename = display_name + '.ipa'
        log.debug('Generating "{}"'.format(ipa_filename))
        try:
            app_name = file_dict['app']
            for key, value in file_dict.items():
                from_dir = os.path.join(path, key)
                to_dir = os.path.join(path, app_name, value)
                if key != 'app':
                    shutil.move(from_dir, to_dir)
            
            target_dir = './Payload'
            zip_args = ('zip', '-qr', os.path.join(os.getcwd(), ipa_filename), target_dir) # ./Pumpkin/[AppName].ipa
            subprocess.check_call(zip_args, cwd=OUTPUT_DIR.name)
            log.halt("check")
            #shutil.rmtree(PAYLOAD_PATH)
        except Exception as e:
            log.error(e)

