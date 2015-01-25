from Queue import PriorityQueue
from collections import namedtuple
from cherrypy.process.plugins import SimplePlugin
import cherrypy
from cherrypy.process import wspbus, plugins
import sqlite3
import json
import time
from Plugins.PluginBase import PluginBase


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

epg_sql = """CREATE  TABLE IF NOT EXISTS "main"."epg"
              ("epg_event_id" DOUBLE PRIMARY KEY  NOT NULL  UNIQUE ,
              "epg_event_start" DOUBLE NOT NULL ,
              "epg_event_duration" DOUBLE NOT NULL ,
              "epg_event_current_time" DOUBLE NOT NULL ,
              "epg_event_title" TEXT,
              "epg_event_description" TEXT,
              "epg_event_description_extended" TEXT,
              "epg_event_service_ref" INTEGER NOT NULL ,
              "epg_event_deleted" INTEGER NOT NULL  DEFAULT 0)"""


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

MessageRequest = namedtuple('MessageRequest', 'script, action, data')

class DBHandler(PluginBase):

    DATABASE_NAME = 'dreamboxserver.sqlite'

    def __init__(self, bus):

        super(DBHandler, self).__init__(bus, name='db_handler')

        sqldb = sqlite3.connect(DBHandler.DATABASE_NAME, timeout=10)
        cursor = sqldb.cursor()
        # create tables
        cursor.execute(b_sql)
        cursor.execute(ch_sql)
        cursor.execute(epg_sql)
        sqldb.commit()
        sqldb.close()
        # A queue to store any responses we may want
        self.response_queue = PriorityQueue()
        # Add our callbacks
        self.action_dict.update ({'bouquet_update': DBHandler.bouquet_update,
                                  'get_bouquets': DBHandler.get_bouquets,
                                  'get_channels': DBHandler.get_bouquet_channels,
                                  'get_all_channels': DBHandler.get_all_channels,
                                  'epg_update': DBHandler.epg_update,
                                  'epg_now_next': DBHandler.epg_now_next,
                                  'update_now_next': DBHandler.update_now_next})

    def start(self):
        self.bus.log('Waiting for db stuff')

    def stop(self):
        self.bus.log('Cant be arsed anymore')
        self.bus.unsubscribe('db_handler', self.dispatch)


    def epg_update(self, bouquets):
        '''
        Updates the npuquet records with the bpuquests passed in as a parameter. Passes in a dict where the key is
        the bpuquet sref and the value is the associated list of channels
        :param bouquets:
        :return:
        '''

        self.bus.log('Got something  ' + str(bouquets))


        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute('DELETE FROM epg')
        curs.execute('VACUUM')
        db.commit()


        curs.executemany("""INSERT INTO epg (epg_event_id, epg_event_start, epg_event_duration,
                            epg_event_title, epg_event_description, epg_event_description_extended,
                            epg_event_service_ref) VALUES (?, ?, ?, ?, ?, ?, ?)""", bouquets.data)
        db.commit()
        db.close()


    def bouquet_update(self, bouquets):

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute('DELETE FROM bouquet')
        curs.execute('DELETE FROM channel')
        curs.execute('VACUUM')
        db.commit()

        for k, v in bouquets.data:
            last_id = curs.execute('INSERT INTO bouquet(bo_service_ref, bo_service_name) VALUES(?, ?)', (k, v)).lastrowid
            c = bouquets.data[(k,v)]
            d = [(last_id, a , b) for a, b in c]
            self.bus.log(str(d))
            curs.executemany("""INSERT INTO channel (ch_bo_id, ch_service_ref, ch_service_name) VALUES (?,?,?)""", d)
        db.commit()
        db.close()

    def update_now_next(self, data):

        script, action, data = data
        #split the data into db channel id, and epg now next data
        if data:
            db = sqlite3.connect(DBHandler.DATABASE_NAME)
            curs = db.cursor()
            curs.execute('DELETE FROM now_next')
            curs.execute('VACUUM')
            db.commit()
            curs.executemany("""INSERT INTO now_next (nn_ch_id, nn_title, nn_sref, nn_start, nn_event_id, nn_description, nn_description_extended) VALUES (?,?,?,?,?,?,?)""", data)
            db.commit()
            db.close()



    def get_bouquets(self, data):
        script, action, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute('''SELECT bo_service_name, bo_service_ref, bo_id FROM bouquet  WHERE bo_deleted = 0''')
        rows  = curs.fetchall()
        data = json.dumps(dict([(row[1], (row[0], row[2])) for row in rows]))
        response = MessageResponse(1, script, action, data)
        cherrypy.engine.publish(script, response)

    def get_bouquet_channels(self, data):
        script, action, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        self.bus.log(data)
        curs.execute("""SELECT ch_service_name, channel.ch_service_ref, ch_id from channel where ch_deleted = 0 and ch_bo_id = ?""", [data])
        rows  = curs.fetchall()
        data = json.dumps(dict([(row[0], (row[1], row[2])) for row in rows]))
        response = MessageResponse(1, script, action, data)
        cherrypy.engine.publish(script, response)

    def epg_now_next(self, data):
        """
        :param sRef: Gets the current and next event on the given channel
        :return:
        """
        sql = """select * from (
                        select epg_event_title, epg_event_service_ref, epg_event_start, epg_event_id, epg_event_description, epg_event_description_extended
                        from epg
                        where epg_event_start < ?  and epg_event_start + epg_event_duration > ?
                        and epg_event_service_ref = ?
                        union
                        select epg_event_title, epg_event_service_ref, epg_event_start, epg_event_id, epg_event_description, epg_event_description_extended
                        from epg
                        where epg_event_start > ?
                        and epg_event_service_ref = ? ) a
                        order by epg_event_start LIMIT 2"""

        script, action, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        now = int(time.time())
        curs.execute(sql, [now, now, data[1], now, data[1]])
        rows = curs.fetchall()
        if rows:
            data = [(data[0], row[0], row[1], row[2], row[3], row[4], row[5] ) for row in rows]
        else:
            data = []
        response = MessageResponse(1, script, action, data)
        cherrypy.engine.publish(script, response)

    def get_epg_last_channels_times(self, data):
        """
        Returns the last start time for each channel in the databasse. This can be used to get the epg records
        from the dreambox since we last updated, instead of continually fetching the complete epg
        :param data:
        :return:
        """
        script, action, data = data

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        self.bus.log(data)
        curs.execute("""SELECT ch_service_name, channel.ch_service_ref, ch_id from channel where ch_deleted = 0 and ch_bo_id = ?""", [data])
        rows  = curs.fetchall()
        data = json.dumps(dict([(row[0], (row[1], row[2])) for row in rows]))
        response = MessageResponse(1, script, action, data)
        cherrypy.engine.publish(script, response)

    def get_all_channels(self, request):
        """
        Received a request from the bus in response to a publish elsewhere
        Response is a 3-tuple in the format (script, action, data) where
        script = script that sent the request and requires a response
        action = THe action on the script to process the response
        data = the actual data to process
        :param request:
        :return:
        """

        script, action, data = request

        db = sqlite3.connect(DBHandler.DATABASE_NAME)
        curs = db.cursor()
        curs.execute("""SELECT channel.ch_service_ref, ch_id from channel where ch_deleted = 0""")
        rows  = curs.fetchall()

        data = json.dumps(dict([(row[0], row[1]) for row in rows]))
        response = MessageResponse(priority=2, script=script, action=action, data=data)

        cherrypy.engine.publish(script, response)







if __name__ == '__main__':
    DBHandler(cherrypy.engine)