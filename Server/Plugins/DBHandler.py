

from cherrypy.process.plugins import SimplePlugin
import cherrypy
from cherrypy.process import wspbus, plugins
import sqlite3
import json


b_sql = """ CREATE TABLE IF NOT EXISTS
            bouquet(
            bo_id INTEGER PRIMARY KEY,
            bo_service_name TEXT  NOT NULL,
            bo_service_ref TEXT  NOT NULL,
            bo_deleted DEFAULT 0)
"""

ch_sql = """CREATE  TABLE IF NOT EXISTS
            channel ("ch_id" INTEGER PRIMARY KEY  NOT NULL ,
            "ch_service_name" TEXT NOT NULL ,
            "ch_service_ref" TEXT NOT NULL ,
            "ch_order" INTEGER,
            "ch_bo_id" INTEGER,
            "ch_deleted" INTEGER NOT NULL  DEFAULT 0)"""


class Response(object):

    def __init__(self, priority, where, data):
        self.priority = priority
        self.where = where
        self.data = data
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

class DBHandler(SimplePlugin):

    DATABASE_NAME = 'dreamboxserver.sqlite'

    def __init__(self, bus):

        super(DBHandler, self).__init__(bus)


        sqldb = sqlite3.connect(DBHandler.DATABASE_NAME, timeout=10)
        cursor = sqldb.cursor()
        # create tables
        cursor.execute(b_sql)
        cursor.execute(ch_sql)
        sqldb.commit()
        sqldb.close()





    def start(self):
        self.bus.log('Waiting for db stuff')
        self.bus.subscribe('bouquet_update', self.bouquet_update)
        self.bus.subscribe('bouquet_request', self.get_bouquets)
        self.bus.subscribe('channel_request', self.get_channels)
        self.bus.subscribe('all_channel_request', self.get_all_channels)
        #todo here, just have one subscribe and get a function to parse the request and distribute to the response
        self.bus.subscribe('db_handler', self.dispatch)

    def dispatch(self):
        pass


    def stop(self):
        self.bus.log('Cant be arsed anymore')
        self.bus.unsubscribe('bouquet_update', self.bouquet_update)


    def bouquet_update(self, bouquets):
        '''
        Updates the npuquet records with the bpuquests passed in as a parameter. Passes in a dict where the key is
        the bpuquet sref and the value is the associated list of channels
        :param bouquets:
        :return:
        '''

        self.bus.log('Got something  ' + str(bouquets))

        #1. get the bouquest in a list and update as requeired, if channels need updating flag
        b = [(k, v) for k, v in bouquets]
        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute('DELETE FROM bouquet')
        curs.execute('DELETE FROM channel')
        curs.execute('VACUUM')
        db.commit()

        for k, v in b:
            last_id = curs.execute('INSERT INTO bouquet(bo_service_ref, bo_service_name) VALUES(?, ?)', (k, v)).lastrowid
            c = bouquets[(k,v)]
            d = [(last_id, a , b) for a, b in c]
            self.bus.log(str(d))
            curs.executemany("""INSERT INTO channel (ch_bo_id, ch_service_name, ch_service_ref) VALUES (?,?,?)""", d)
        db.commit()
        db.close()


    def get_bouquets(self, data):
        #TODO implement where - should be bouquet_response
        where, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute('''SELECT bo_service_name, bo_service_ref, bo_id FROM bouquet  WHERE bo_deleted = 0''')
        rows  = curs.fetchall()

        data = json.dumps(dict([(row[1], (row[0], row[2])) for row in rows]))

        response = Response(1, where, data)
        cherrypy.engine.publish('response', response)

    def get_channels(self, data):
        #TODO implement where - should be bouquet_response
        where, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        self.bus.log(data)
        curs.execute("""SELECT ch_service_name, channel.ch_service_ref, ch_id from channel where ch_deleted = 0 and ch_bo_id = ?""", [data])
        rows  = curs.fetchall()

        data = json.dumps(dict([(row[0], (row[1], row[2])) for row in rows]))

        response = Response(1, where, data)
        cherrypy.engine.publish('response', response)

    def get_all_channels(self, data):
        #TODO implement where - should be bouquet_response
        where, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        self.bus.log(data)
        curs.execute("""SELECT channel.ch_service_ref, ch_id from channel where ch_deleted = 0""")
        rows  = curs.fetchall()

        data = json.dumps(dict([(row[0], row[1]) for row in rows]))
        #todo need to update to add an additional param in response for the channel to publish to ie now_next_monitor
        response = Response(2, where, data)

        cherrypy.engine.publish('now_next_monitor', response)







if __name__ == '__main__':
    DBHandler(cherrypy.engine)