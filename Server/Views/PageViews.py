from Queue import PriorityQueue
from collections import namedtuple
import os

from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy

from Plugins.Transcoder import Transcoder
from Plugins.DBHandler import DBHandler
from Plugins.BouquetMonitor import BouquetMonitor
from Plugins.EPGMonitor import EPGMonitor
from Plugins.MediaServer import MediaServer
from Plugins.NowNextMonitor import NowNextMonitor


MessageRequest = namedtuple('MessageRequest', 'script, action, data', verbose=False)


class PageBase(object):
    # TODO Implement this in other page views

    # Record any misssing params
    missing_params = {}
    # Params that are not the correct format
    incorrect_params = {}
    # Params that are ok. Stored in dict se we are not constantly going to the server and fetching values.
    # Just update this after a value has been saved ok in the database
    params = {}

    @classmethod
    def check_params(cls, params):
        PageBase.missing_params.update(dict([(cls.__name__, k) for k, v in params.iteritems() if len(v) == 0]))
        #TODO add to params as theyt are ok - Incorrrect checked as we update them - Do we actually need tyhat as we can check before saving <-- Yes do this


class API(PageBase):
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
        # todo validate sref
        cherrypy.engine.publish('db_handler', MessageRequest('api', 'get_channels', bouquet_id))
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return resp.data if resp.action == 'get_channels' else self.q.put(resp)
        return None

    @cherrypy.expose
    def get_channel_now_next(self, channel_id):
        # todo validate sref
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


class Stream(PageBase):

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
        # todo need to publish methods here to stop, then start so we dont return straight away
        cherrypy.engine.publish('transcoder', MessageRequest('stream', 'start_transcoder', '1'))
        for i in xrange(1, 100, 1):
            cherrypy.log('waiting for response response')
            resp = self.q.get()
            cherrypy.log('got response')
            if resp.action == 'start_transcoder':
                raise cherrypy.HTTPRedirect('http://localhost:28090/live_audio1.mkv')
            else:
                self.q.put(resp)
        return None


    @cherrypy.expose
    def audio2(self):

        raise cherrypy.HTTPRedirect('http://localhost:28090/live_audio2.mkv')


class About(PageBase):

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/about.html', lookup=mylookup)
        return index.render()


class Player(PageBase):

    def __init__(self, params):
        super(Player, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())
        Player.check_params(self.params)

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/player.html', lookup=mylookup)
        return index.render()


class Dreambox(PageBase):

    def __init__(self, params):
        super(Dreambox, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())
        Dreambox.check_params(self.params)


    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/dreambox.html', lookup=mylookup)
        return index.render(**self.params)


class FFMPEG(PageBase):

    def __init__(self, params):

        super(FFMPEG, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/ffmpeg.html', lookup=mylookup)
        return index.render(**self.params)


class FFServer(PageBase):

    def __init__(self, params):

        super(FFServer, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/ffserver.html', lookup=mylookup)
        return index.render(**self.params)


class Plex(PageBase):

    def __init__(self, params):
        super(Plex, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/plex.html', lookup=mylookup)
        return index.render(**self.params)


class DreamboxServer(PageBase):

    def __init__(self, params):

        super(DreamboxServer, self).__init__()
        self.params = dict((k, v) for item in params for (k, v) in item.iteritems())

    @cherrypy.expose
    def index(self):
        # todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template(filename=os.path.abspath('.') + '/html/dreamboxserver.html', lookup=mylookup)
        return index.render(**self.params)


class Home(PageBase):

    def __init__(self):

        super(Home, self).__init__()
        self.q = PriorityQueue()
        DBHandler(cherrypy.engine).subscribe()
        cherrypy.engine.subscribe('server', self.dispatch)
        self.get_params()

    def start_webapp_handlers(self, params):
        """
        Start the page handlers. We don't start the Feeds, Stream or API Handlers here
        as we don' know if all the required params are present. ie Just provide a web app.
        Pass the corresponding params in to each handler . The handler will check its own params and add to the
        appropriate list if any are missing or incorrect

        Finally, try and start the service handlers
        """
        Home.Player = Player()
        Home.Dreambox = Dreambox(params.get('dreambox', {}))
        Home.FFMPEG = FFMPEG(params.get('ffmpeg', {}))
        Home.FFServer = FFServer(params.get('ffserver', {}))
        Home.Plex = Plex(params.get('plex', {}))
        Home.DreamboxServer = DreamboxServer(params.get('dreamboxserver', {}))
        Home.About = About()
        self.start_service_handlers()

    def start_service_handlers(self):
        """
        Start the actual handlers for the service if we dont have ay values missing or incorrect
        At this point we can also start up our plugins that provide the
        interface between the dreambox and FFMPEG/Server

        """
        if not Home.missing_params:
            Home.API = API()
            Home.Feeds = Feeds(path='192.168.1.100', host=80)
            Home.Stream = Stream(path='192.168.1.100', host=80)

            BouquetMonitor(cherrypy.engine).subscribe()
            EPGMonitor(cherrypy.engine).subscribe()
            MediaServer(cherrypy.engine).subscribe()
            NowNextMonitor(cherrypy.engine).subscribe()
            Transcoder(cherrypy.engine).subscribe()

    def get_params(self):
        """
        Get the parameters currently stored in the database and pass to the webapp hadlers to initialise their
        contents
        """
        # see if we have a ip for the dreambox

        cherrypy.engine.publish('db_handler', MessageRequest('server', 'get_params', None))
        params = None
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            if resp.action == 'get_params':
                params = resp.data
                break
            else:
                self.q.put(resp)

        if params:
            self.start_webapp_handlers(params)
        else:
            return None


    def dispatch(self, message):

        if isinstance(message, tuple):
            pass
        else:
            # we are waiting  for something
            self.q.put(message)


    @cherrypy.expose
    def index(self):
        """
        The Home page of the app. If we have all the required params, then display the dashboard,
        otherwise display an error screen and inform the user of the missing stuff
        """
        import os

        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])

        if Home.missing_params:
            index = Template(filename=os.path.abspath('.') + '/html/index_missing_vals.html', lookup=mylookup)
            cherrypy.log(str(Home.missing_params))
        else:
            index = Template(filename=os.path.abspath('.') + '/html/index.html', lookup=mylookup)

        return index.render(missing=Home.missing_params)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def update_config(self, key, value):
        # TODO Need to check here if value is empty, return false so we can display an error
        cherrypy.engine.publish('db_handler', MessageRequest('server', 'update_param', (key, value)))
        resulq = None
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            if resp.action == 'update_param':
                result = resp.data
                break
            else:
                self.q.put(resp)
        if result:

            return {'result': True}
        else:
            return {'result': False}
