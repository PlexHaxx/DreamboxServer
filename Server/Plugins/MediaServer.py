
from PluginBase import PluginBase
from StringIO import StringIO
import cherrypy
import subprocess




class MediaServer(PluginBase):

    # TODO Add a subscribe, change disoatch to another method to start server, then dispatch to handle messages
    # TODo change to monitor so it can run every x seconds and get page date, then post messages to FFServer screen, this then receives an ajax call to pull the details from the
    # TODO queue - maybe put in a list. Client keeps track of last message it has received, so multiple  users can access the page, or isnt this needed?
    # TODO The trace thng blocks, but do we need it anyway. Just monitor the web page and get the details from there
    # TODO Do we need to monitor ffmpeg though? Maybe output to file and monitor that. We coud tell its working as we will have a connection in ffserver.

    def __init__(self, bus):
        super(MediaServer, self).__init__(bus, name='ffserver', frequency=5)
        self.started = False
        self.process = None
        self.host = '127.0.0.1'
        self.port = 28090
        self.callback = self.monitor
        self.action_dict.update({})

    def monitor(self):
        # get the stat page
        page = self.get_ffsever_stat_page(self.host, self.web)

        # parse it into a dict

        # Send it to the FFServer view to pass to client

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

    def get_ffsever_stat_page(self, host, web):
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.WRITEDATA, buffer)
        url = 'http://{}:{}/stat.html'.format(host, web)
        c.setopt(c.URL, url)
        c.setopt(c.POSTFIELDS, postfields)
        c.perform()
        c.close()
        return buffer.getvalue()
