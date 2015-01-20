

from cherrypy.process.plugins import SimplePlugin
import cherrypy
from cherrypy.process import wspbus, plugins
import sqlite3


b_sql = """ CREATE TABLE IF NOT EXISTS
            bouquets(
            bou_id INTEGER PRIMARY KEY,
            bo_service_name TEXT  NOT NULL,
            bo_service_ref TEXT  NOT NULL,
            bou_deleted DEFAULT 0)
"""

ch_sql = """CREATE  TABLE "main"."channel" ("ch_id" INTEGER PRIMARY KEY  NOT NULL , "ch_service_name" TEXT NOT NULL , "ch_service_ref" TEXT NOT NULL , "ch_deleted" INTEGER NOT NULL  DEFAULT 0)"""


class DBHandler(SimplePlugin):

    def __init__(self, bus):

        super(DBHandler, self).__init__(bus)
        try:
            sqldb = sqlite3.connect('dreamboxserver', timeout=10)
            cursor = sqldb.cursor()
            # create tables
            cursor.execute(b_sql)
            sqldb.commit()
        except Exception as e:
            print e




    def start(self):
        self.bus.log('Waiting for db stuff')
        self.bus.subscribe('bouquet_update', self.bouquet_update)

    def stop(self):
        self.bus.log('Cant be arsed anymore')
        self.bus.unsubscribe('bouquet_update', self.bouquet_update)


    def bouquet_update(self, bouquets):

        self.bus.log('Got something  ' + str(bouquets))


if __name__ == '__main__':
    DBHandler(cherrypy.engine)