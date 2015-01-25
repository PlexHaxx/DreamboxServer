
from PluginBase import PluginBase
import cherrypy
import subprocess




class MediaServer(PluginBase):

    # TODO Add a subscribe, change disoatch to another method to start server, then dispatch to handle messages
    # TODo change to monitor so it can run every x seconds and get page date, then post messages to FFServer screen, this then receives an ajax call to pull the details from the
    # TODO queue - maybe put in a list. Client keeps track of last message it has received, so multiple  users can access the page, or isnt this needed?
    # TODO The trace thng blocks, but do we need it anyway. Just monitor the web page and get the details from there
    # TODO Do we need to monitor ffmpeg though? Maybe output to file and monitor that. We coud tell its working as we will have a connection in ffserver.

    def __init__(self, bus):
        super(MediaServer, self).__init__(bus, name='ffserver')
        self.started = False
        self.process = None

    def start(self):
        self.bus.log('Starting ffserver')
        self.startFFServer()

    def startFFServer(self,):
        cherrypy.log('sd')
        self.process = subprocess.Popen(['ffserver', '-d'],
                                            bufsize=4096,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    def stop(self):
        self.bus.log('Stoppping ffserver')
        self.bus.unsubscribe('ffserver', self.dispatch)
        if self.process is not None:
            self.process.kill()
