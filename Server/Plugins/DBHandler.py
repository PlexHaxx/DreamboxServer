

from cherrypy.process.plugins import SimplePlugin
import cherrypy
from cherrypy.process import wspbus, plugins

class DBHandler(SimplePlugin):

    def __init__(self, bus):

        super(DBHandler, self).__init__(bus)
        self.name = 'DB Handler'


    def start(self):
        self.bus.log('Waiting for db stuff')
        self.bus.subscribe('bouquet_update', self.bouquet_update)

    def stop(self):
        self.bus.log('Cant be arsed anymore')
        self.bus.unsubscribe('bouquet_update', self.bouquet_update)


    def bouquet_update(self, bouquets):

        self.bus.log('Got something  ' + str(bouquets))