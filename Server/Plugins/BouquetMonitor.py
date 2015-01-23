from collections import namedtuple
import pycurl
from StringIO import StringIO
from urllib import urlencode
from BeautifulSoup import BeautifulSoup


import cherrypy

MessageRequest = namedtuple('MessageRequest', 'script, action, data')

class BouquetMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self, bus):
        super(BouquetMonitor, self).__init__(bus, callback=None, frequency=10)
        self.host = '192.168.1.252'
        self.port = 80
        self.callback = self.monitor
        self.name = 'Bouquets Monitor'
        self.old_bouquets = None
        self.old_channels = {}


    def monitor(self):
        self.bus.log('in thread')
        self.process_bouquets(self.host, self.port)

    def process_bouquets(self, host, port):

        update = False

        channels = {}

        # this just gets a list of bouquets
        bouquet_xml = self.get_bouquets_from_receiver(host, port)
        if self.old_bouquets != bouquet_xml or self.old_bouquets is None:
            bouquets = self.parse_xml_for_bouquets(bouquet_xml)
            update = True
        else:
            bouquets = self.parse_xml_for_bouquets(self.old_bouquets)

        #loop through the bouquets and get the channels. Save them all, and update all if one has changed
        for k, v in bouquets:
            channel_xml = self.get_channels_from_service(host, port, k)
            # have we got a new bouquet with empty channels
            if (k, v) not in self.old_channels:
                # Add channels
                channels[(k, v)] = self.parse_xml_for_channels((k,v), channel_xml)
                update = True
            else:
                if self.old_channels[(k, v)] != channel_xml:
                    update = True
                channels[(k, v)] = self.parse_xml_for_channels((k,v), channel_xml)

        if update:
            cherrypy.engine.publish('db_handler', MessageRequest('bouquet_monitor', 'bouquet_update', channels))


    def get_bouquets_from_receiver(self, host, port):

        url = 'http://{}:{}/web/getservices'.format(host, port)
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
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
    d = BouquetMonitor()
    d.process_bouquets('192.168.1.252', 80)