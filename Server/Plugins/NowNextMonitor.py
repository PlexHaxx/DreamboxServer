from Queue import PriorityQueue
import pycurl
from StringIO import StringIO
from urllib import urlencode
from BeautifulSoup import BeautifulSoup

import cherrypy

class NowNextMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self, bus ):
        super(NowNextMonitor, self).__init__(bus, callback=None, frequency=5)
        self.host = '192.168.1.252'
        self.port = 80
        self.callback = self.monitor
        self.name = 'Now Next Monitor'
        self.q = PriorityQueue()

        cherrypy.engine.subscribe('now_next_monitor', self.handle_response)


    def handle_response(self, response):
        self.q.put(response)


    def monitor(self):
        self.bus.log('in thread now_next')
        db_channels = self.get_channels_from_db(self.host, self.port)
        self.get_now_next(db_channels)

    def get_channels_from_db(self, host, port):


        cherrypy.engine.publish('all_channel_request', ('get_something', None))
        for i in xrange(1, 100, 1):
            resp = self.q.get()
            return resp.data if resp.where == 'get_something' else self.q.put(resp)
        return None

    def get_now_next(self, host, port, sRef='1:0:1:1933:7FF:2:11A0000:0:0:0:'):
        buffer = StringIO()
        c = pycurl.Curl()

        url = 'http://{}:{}/web/epgservicenow'.format(host, port)
        c.setopt(c.URL, url)
        post_data = {'sRef': sRef}
        postfields = urlencode(post_data)
        c.setopt(c.POSTFIELDS, postfields)
        c.perform()
        url = 'http://{}:{}/web/epgservicenext'.format(host, port)
        c.setopt(c.URL, url)
        c.perform()
        print buffer.getvalue()
        c.close()
        return buffer.getvalue()



    def parse_xml_for_bouquets(self, xml):

        e2service_details = lambda y: y.findAll(['e2servicereference', 'e2servicename'])
        e2service = lambda y: y.findAll('e2service')

        self.old_bouquets = xml
        bouquet_xml = BeautifulSoup(self.old_bouquets)
        bouquets = [(a[0].text, a[1].text) for a in [e2service_details(x) for x in e2service(bouquet_xml)]]
        return bouquets


    def parse_xml_for_channels(self, bouquet,  xml):

        e2service_details = lambda y: y.findAll(['e2servicereference', 'e2servicename'])
        e2service = lambda y: y.findAll('e2service')

        self.old_channels[bouquet] = xml
        channel_xml = BeautifulSoup(self.old_channels[bouquet])
        channels = [(a[0].text, a[1].text) for a in [e2service_details(x) for x in e2service(channel_xml)]]
        return channels



    def get_channels_from_service(self, host, web, sRef=None, show_epg=False):

        url = 'http://{}:{}/web/getservices'.format(host, web)
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        post_data = {'sRef': sRef}
        postfields = urlencode(post_data)
        c.setopt(c.POSTFIELDS, postfields)
        c.perform()
        c.close()
        return buffer.getvalue()


    def get_channels_from_epg(host, web, bRef):

        url = 'http://{}:{}/web/epgbouquet'.format(host, web)
        data = {'bRef': bRef}
        soup = get_data((url, data))
        results = get_events(soup)
        return results



if __name__ == '__main__':
    d = NowNextMonitor(None)
    print d.get_now_next('192.168.1.252', 80)


    '''
    <?xml version="1.0" encoding="UTF-8"?>
<e2eventlist>
	<e2event>
		<e2eventid>37344</e2eventid>
		<e2eventstart>1421906400</e2eventstart>
		<e2eventduration>11700</e2eventduration>
		<e2eventcurrenttime>1421913472</e2eventcurrenttime>
		<e2eventtitle>Breakfast</e2eventtitle>
		<e2eventdescription></e2eventdescription>
		<e2eventdescriptionextended>The latest news, sport, business and weather from the BBC's Breakfast team. Also in HD. [S] Including regional news at 25 and 55 minutes past each hour.</e2eventdescriptionextended>
		<e2eventservicereference>1:0:1:1933:7FF:2:11A0000:0:0:0:</e2eventservicereference>
		<e2eventservicename>BBC One Yorks</e2eventservicename>
	</e2event>
</e2eventlist>
<?xml version="1.0" encoding="UTF-8"?>
<e2eventlist>
	<e2event>
		<e2eventid>49044</e2eventid>
		<e2eventstart>1421918100</e2eventstart>
		<e2eventduration>2700</e2eventduration>
		<e2eventcurrenttime>1421913472</e2eventcurrenttime>
		<e2eventtitle>Wanted Down Under</e2eventtitle>
		<e2eventdescription></e2eventdescription>
		<e2eventdescriptionextended>Series in which families try out life overseas. A mum with ME hopes Australia will improve her health and family life, so the family spend a week living in Adelaide. Also in HD. [S].</e2eventdescriptionextended>
		<e2eventservicereference>1:0:1:1933:7FF:2:11A0000:0:0:0:</e2eventservicereference>
		<e2eventservicename>BBC One Yorks</e2eventservicename>
	</e2event>
</e2eventlist>'''