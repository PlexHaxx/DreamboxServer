from Queue import PriorityQueue
from collections import namedtuple


import cherrypy

MessageRequest = namedtuple('MessageRequest', 'script, action, data', verbose=False)
"""
Script = Script that sent the message
action = The action to invoke on the receiver
data = The data, if any to pass to the receiver
"""


class MediaServer(cherrypy.process.plugins.SimplePlugin):

    # TODO Add a subscribe, change disoatch to another method to start server, then dispatch to handle messages
    # TODo change to monitor so it can run every x seconds and get page date, then post messages to FFServer screen, this then receives an ajax call to pull the details from the
    # TODO queue - maybe put in a list. Client keeps track of last message it has received, so multiple  users can access the page, or isnt this needed?

    def __init__(self, bus ):
        super(MediaServer, self).__init__(bus)
        self.name = 'FFServer'
        self.q = PriorityQueue()
        self.started = False
        self.process = None

    def start(self):
        self.bus.log('Starting ffserver')
        cherrypy.engine.subscribe('ffserver', self.dispatch)
        self.dispatch()
        #self.Trace(self.process)

    def Trace(self, proc):

        if proc is not None:
            while proc.poll() is None:
                try:
                    line = proc.stdout.readline()
                    if line:
                        if 'started' in line and self.started is False :
                            self.started = True
                        # Process output here

                        self.bus.log('FFServer ' + line)
                except:
                    pass

    def dispatch(self,):
        cherrypy.log('sd')

        import subprocess
        self.process = subprocess.Popen(['ffserver', '-d'],
                                            bufsize=4096,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    def stop(self):
        self.bus.log('Stoppping ffserver')
        self.bus.unsubscribe('ffserver', self.dispatch)
        if self.process is not None:
            self.process.kill()
