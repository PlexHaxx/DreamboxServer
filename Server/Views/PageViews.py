
from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import os


class Feeds():

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):

        channels = [('audio1', 'http://localhost:28090/live_audio1.mkv'), ('audio1', 'http://localhost:28090/live_audio2.mkv' )]
        return channels

class Stream():

    @cherrypy.expose
    def audio1(self):

        raise cherrypy.HTTPRedirect('http://localhost:28090/live_audio1.mkv')

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

class Bouquets():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/bouquets.html', lookup=mylookup)
        return index.render()

class Dreambox():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/dreambox.html', lookup=mylookup)
        return index.render()

class FFMPEG():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/ffmpeg.html', lookup=mylookup)
        return index.render()

class FFServer():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/ffserver.html', lookup=mylookup)
        return index.render()

class Plex():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/plex.html', lookup=mylookup)
        return index.render()

class DreamboxServer():

    @cherrypy.expose
    def index(self):
        #todo Some subscribe call here and elsewhere to put message on bus we have selected something and call appropriate plugin
        mylookup = TemplateLookup(directories=[os.path.abspath('.') + '/html'])
        index = Template (filename=os.path.abspath('.') + '/html/dreamboxserver.html', lookup=mylookup)
        return index.render()