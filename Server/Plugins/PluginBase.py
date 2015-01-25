from Queue import PriorityQueue
from collections import namedtuple
import cherrypy


MessageRequest = namedtuple('MessageRequest', 'script, action, data', verbose=False)
"""
Script = Script that sent the message
action = The action to invoke on the receiver
data = The data, if any to pass to the receiver
"""


class PluginBase(cherrypy.process.plugins.Monitor):



    def __init__(self, bus, name, callback=None, frequency=None ):
        super(PluginBase, self).__init__(bus, callback=callback, frequency=frequency)
        self.name = name

        # Queue for incoming jobs
        self.q = PriorityQueue()

        # dict of actions and their associated functions. A sub class should populate this with the
        # methods that should be called when a message is received
        self.action_dict = {}

        # lambda function to run the associated function.
        self.action = lambda x, y, z: x(y, z)

        #subscribe to the channel passed through as a name to listen for requests
        cherrypy.engine.subscribe(name, self.dispatch)

    def dispatch(self, message):

        try:
            if message is not None:
                self.action(self.action_dict[message.action], self, message)
        except KeyError:
            self.q.put(message)


class MessageResponse(object):
    """
    Class to be used to pass data along the bus in response to a particular publish
    priority = Priority of a message. e.g jump to the form of the queue
    script = The script that the response message is for
    action = The action of the script that will process the response message.
    """

    def __init__(self, priority, script, action, data):
        self.priority = priority
        self.script = script
        self.action = action
        self.data = data
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)