
import cherrypy
import os
from mako.template import Template
from mako.lookup import TemplateLookup
from Plugins.BouquetMonitor import BouquetMonitor
from Views.PageViews import Feeds, Dreambox, DreamboxServer, FFServer, FFMPEG, Plex,About, Bouquets, Stream, API
from Plugins.DBHandler import Response
from Plugins.DBHandler import DBHandler
from Queue import PriorityQueue
import time


path = os.path.abspath(os.path.dirname(__file__))
config = {
  'global' : {
    'server.socket_host' : '127.0.0.1',
    'server.socket_port' : 9095,
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

    Feeds = Feeds()
    Stream = Stream()
    Bouquets = Bouquets()
    Dreambox = Dreambox()
    FFMPEG =FFMPEG()
    FFServer = FFServer()
    Plex = Plex()
    DreamboxServer = DreamboxServer()
    About = About()
    BouquetMonitor(cherrypy.engine).subscribe()
    DBHandler(cherrypy.engine).subscribe()
    API = API()




    @cherrypy.expose
    def index(self):
        import os
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/index.html', lookup=mylookup)

        return index.render()






cherrypy.quickstart(Home(), config=config)
"""


ffmpeg  -i http://192.168.1.252:8001/1:0:19:1B1D:802:2:11A0000:0:0:0: -override_ffserver -map 0:0 -map 0:15 -s 1920x1080 -buffer_size 160000000  -vcodec libx264  -crf 30 -pix_fmt yuv420p -vb 1500000  -preset ultrafast  -strict experimental -vf yadif -acodec libfaac -ab 96000 -ac 2  http://192.168.1.100:28090/feed4.ffm


ffmpeg  -i http://192.168.1.252:8001/1:0:19:1B1D:802:2:11A0000:0:0:0: -override_ffserver -map 0:0 -map 0:15 -s 1920x1080 -buffer_size 160000000  -vcodec h264  -flags +loop+mv4 -cmp 256 -partitions +parti4x4+parti8x8+parti4x4+part8x8 -subq 7 -trellis 1 -refs 5 -bf 0  -coder 0 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -qmin 10 -qmax 51 -qdiff 4 -vb 1500000  -preset ultrafast  -strict experimental -vf yadif -acodec libfaac -ab 96000 -ac 2  http://192.168.1.100:28090/feed4.ffm
"""