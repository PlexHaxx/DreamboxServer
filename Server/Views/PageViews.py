from Queue import PriorityQueue
from collections import namedtuple
import itertools
from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import os
import operator
from Plugins.Transcoder import Transcoder
import time


MessageRequest = namedtuple('MessageRequest', 'script, action, data', verbose=False)


class API():

    def __init__(self):
        self.q = PriorityQueue()
        cherrypy.engine.subscribe('api', self.dispatch)

    def dispatch(self, message):

        if isinstance(message, tuple):
            pass
        else:
            # we are waiting  for something
            self.q.put(message)

    @cherrypy.expose
    def index(self):
        return '''Some infor of the call
        get_bouquets = {name, ref}'''

    @cherrypy.expose
    def get_bouquets(self):
        cherrypy.engine.publish('db_handler', MessageRequest('api', 'get_bouquets', None))
        cherrypy.engine.log('after publish')
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return resp.data if resp.action == 'get_bouquets' else self.q.put(resp)
        return None

    @cherrypy.expose
    def get_channels(self, bouquet_id):
        #todo validate sref
        cherrypy.engine.publish('db_handler', MessageRequest('api', 'get_channels', bouquet_id))
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return resp.data if resp.action == 'get_channels' else self.q.put(resp)
        return None

    @cherrypy.expose
    def get_channel_now_next(self, channel_id):
        #todo validate sref
        cherrypy.engine.publish('db_handler', MessageRequest('api', 'get_channel_now_next', channel_id))
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return resp.data if resp.action == 'get_channel_now_next' else self.q.put(resp)
        return None

class Feeds():

    def __init__(self, path, host):

        self.path = path
        self.host = host

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):

        channels = [('audio1', 'http://{}:{}/live_audio1.mkv'.format(self.path, self.host)), 
                           ('audio2', 'http://{}:{}/live_audio2.mkv'.format(self.path, self.host))]
        return channels

class Stream():

    def __init__(self, path, host):

        self.path = path
        self.host = host
        self.q = PriorityQueue()
        cherrypy.engine.subscribe('stream', self.dispatch)

    def dispatch(self, message):

        if isinstance(message, tuple):
            pass
        else:
            # we are waiting  for something
            self.q.put(message)

    @cherrypy.expose
    def audio1(self):
        #todo need to publish methods here to stop, then start so we dont return straight away
        cherrypy.engine.publish('transcoder', MessageRequest('stream', 'start_transcoder', '1'))
        for i in xrange(1, 100, 1):
            cherrypy.log('waiting for response response')
            resp = self.q.get()
            cherrypy.log('got response')
            if resp.action == 'start_transcoder' :
                raise cherrypy.HTTPRedirect('http://localhost:28090/live_audio1.mkv')
            else:
                self.q.put(resp)
        return None



    @cherrypy.expose
    def audio2(self):

        raise cherrypy.HTTPRedirect('http://localhost:28090/live_audio2.mkv')



class About():


    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/about.html', lookup=mylookup)
        return index.render()

class Player():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/player.html', lookup=mylookup)
        return index.render()

class Dreambox():

    def __init__(self, params):
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/dreambox.html', lookup=mylookup)
        return index.render(**self.params)

class FFMPEG():

    def __init__(self, params):
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/ffmpeg.html', lookup=mylookup)
        return index.render(**self.params)

class FFServer():

    def __init__(self, params):
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/ffserver.html', lookup=mylookup)
        return index.render(**self.params)

class Plex():

    def __init__(self, params):
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/plex.html', lookup=mylookup)
        return index.render(**self.params)

class DreamboxServer():

    def __init__(self, params):
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/dreamboxserver.html', lookup=mylookup)
        return index.render(**self.params)