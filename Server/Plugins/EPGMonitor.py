from Queue import PriorityQueue
from collections import namedtuple
import json
import pycurl
from StringIO import StringIO
from urllib import urlencode
from BeautifulSoup import BeautifulSoup

import cherrypy

MessageRequest = namedtuple('MessageRequest', 'script, action, data', verbose=False)


class EPGMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self, bus ):
        super(EPGMonitor, self).__init__(bus, callback=None, frequency=120)
        self.host = '192.168.1.252'
        self.port = 80
        self.callback = self.monitor
        self.name = 'EPG Monitor'
        self.q = PriorityQueue()

        cherrypy.engine.subscribe('epg_monitor', self.dispatch)


    def dispatch(self, data):

        if isinstance(data, tuple):
            pass
        else:
            self.q.put(data)


    def monitor(self):
        self.bus.log('in thread epg monitor')
        db_channels = self.get_channels_from_db(self.host, self.port)

        epg = self.get_epg_for_all_channels(self.host, self.port, db_channels)
        events = self.parse_xml_for_epg(epg)
        cherrypy.engine.publish('db_handler', MessageRequest('epg_monitor', 'epg_update', events))



    def get_channels_from_db(self, host, port):

        cherrypy.engine.publish('db_handler', MessageRequest('epg_monitor', 'get_all_channels', None))
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return json.loads(resp.data) if resp.action == 'get_all_channels' else self.q.put(resp)
        return {}





    def parse_xml_for_epg(self, xml):

        e2service_details = lambda y: y.findAll(['e2eventid', 'e2eventstart','e2eventduration','e2eventcurrenttime','e2eventtitle','e2eventdescription','e2eventdescriptionextended','e2eventservicereference','e2servicename',])
        e2service = lambda y: y.findAll('e2event')



        channel_xml = BeautifulSoup(xml)
        channels = [(a[0].text, a[1].text,a[2].text, a[3].text,a[4].text, a[5].
                     text,a[6].text, a[7].text) for a in [e2service_details(x)
                    for x in e2service(channel_xml)]]
        return channels



    def get_epg_for_all_channels(self, host, web, channels):

        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.WRITEDATA, buffer)
        for channel, id in channels.iteritems():
            url = 'http://{}:{}/web/epgservice'.format(host, web)
            c.setopt(c.URL, url)
            post_data = {'sRef': channel}
            postfields = urlencode(post_data)
            c.setopt(c.POSTFIELDS, postfields)

            c.perform()

        c.close()

        return buffer.getvalue()



if __name__ == '__main__':
    d = NowNextMonitor(None)
    print d.get_now_next('192.168.1.252', 80)
