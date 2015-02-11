from Queue import PriorityQueue
import cherrypy
import os
from mako.template import Template
from mako.lookup import TemplateLookup
from Plugins.BouquetMonitor import BouquetMonitor
from Plugins.EPGMonitor import EPGMonitor
from Plugins.Transcoder import Transcoder
from Plugins.PluginBase import MessageRequest
from Views.PageViews import Feeds, Dreambox, DreamboxServer, FFServer, FFMPEG, Plex, About, Player, Stream, API
from Plugins.DBHandler import DBHandler
from Plugins.MediaServer import MediaServer
from Plugins.NowNextMonitor import NowNextMonitor


path = os.path.abspath(os.path.dirname(__file__))
config = {
  'global' : {
    'server.socket_host' : '127.0.0.1',
    'server.socket_port' : 9090,
    'server.thread_pool' : 100
  },
  '/bootstrap' : {
    'tools.staticdir.on'            : True,
    'tools.staticdir.dir'           : os.path.join(path, 'bootstrap'),
    'tools.staticdir.content_types' : {'html': 'text'}
  },
  '/style':{
    'tools.staticdir.on'            : True,
    'tools.staticdir.dir'           : os.path.join(path, 'style')
  }
}



class Home():

    # Start this as we need to query for correct params




    def __init__(self):

        self.q = PriorityQueue()
        DBHandler(cherrypy.engine).subscribe()
        cherrypy.engine.subscribe('server', self.dispatch)
        self.params = {}
        self.missing_params = []
        self.incorrect_params = []
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
        Home.FFMPEG =FFMPEG(params.get('ffmpeg', {}))
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
        if not self.missing_params and self.incorrect_params:
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

        if self.missing_params or self.incorrect_params or not self.params:
                index = Template (filename=os.path.abspath('.') + '/html/index_missing_vals.html', lookup=mylookup)
        else:
            index = Template (filename=os.path.abspath('.') + '/html/index.html', lookup=mylookup)
        return index.render()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def update_config(self, key, value):
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





cherrypy.quickstart(Home(), config=config)
"""


ffmpeg  -i http://192.168.1.252:8001/1:0:19:1B1D:802:2:11A0000:0:0:0: -override_ffserver -map 0:0 -map 0:15 -s 1920x1080 -buffer_size 160000000  -vcodec libx264  -crf 30 -pix_fmt yuv420p -vb 1500000  -preset ultrafast  -strict experimental -vf yadif -acodec libfaac -ab 96000 -ac 2  http://192.168.1.100:28090/feed4.ffm


ffmpeg  -i http://192.168.1.252:8001/1:0:19:1B1D:802:2:11A0000:0:0:0: -override_ffserver -map 0:0 -map 0:15 -s 1920x1080 -buffer_size 160000000  -vcodec h264  -flags +loop+mv4 -cmp 256 -partitions +parti4x4+parti8x8+parti4x4+part8x8 -subq 7 -trellis 1 -refs 5 -bf 0  -coder 0 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -qmin 10 -qmax 51 -qdiff 4 -vb 1500000  -preset ultrafast  -strict experimental -vf yadif -acodec libfaac -ab 96000 -ac 2  http://192.168.1.100:28090/feed4.ffm
"""