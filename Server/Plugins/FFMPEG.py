
from PluginBase import PluginBase
from StringIO import StringIO
import cherrypy
import subprocess




class FFMPEG(PluginBase):

    def __init__(self, bus):
        super(FFMPEG, self).__init__(bus, name='ffmpeg')
        self.started = False
        self.process = None
        self.action_dict.update({})

    def start(self):
        self.bus.log('Starting ffmpeg')
        self.startFFMPEG()

    def startFFMPEG(self):
        cherrypy.log('sd')
        self.process = subprocess.Popen(['ffmpeg', '-i'],
                                            bufsize=4096,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

    def stop(self):
        self.bus.log('Stoppping ffmmpeg')
        self.bus.unsubscribe('ffserver', self.dispatch)
        if self.process is not None:
            self.process.kill()
