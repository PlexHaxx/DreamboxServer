

import pycurl
from StringIO import StringIO
from urllib import urlencode
from BeautifulSoup import BeautifulSoup

import cherrypy

class BouquetMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self, bus ):
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


        bouquet_xml = self.get_bouquets_from_receiver(host, port)
        if self.old_bouquets != bouquet_xml or self.old_bouquets is None:
            bouquets = self.parse_xml_for_bouquets(bouquet_xml)
        else:
            bouquets = self.parse_xml_for_bouquets(self.old_bouquets)

        for k, v in bouquets:
            channel_xml = self.get_channels_from_service(host, port, k)
            if k not in old channels :
                self.old_channels[k] = channel_xml
            else:
                if self.old_channels[k] != channel_xml:
                    #update
                    channels = None
                else:
                    channels = self.parse_xml_for_channels(channel_xml)


        cherrypy.engine.publish('bouquet_update', bouquets)


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
        self.bus.log('updated')
        bouquet_xml = BeautifulSoup(self.old_bouquets)
        bouquets = [(a[0].text, a[1].text) for a in [e2service_details(x) for x in e2service(bouquet_xml)]]
        return bouquets






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

        url = 'http://{}:{}/web/getservices'.format(host, web)
        data = {'sRef': sRef}
        soup = get_data((url, data))
        results = get_service_name(soup, host, web, show_epg)
        return results


    def get_channels_from_epg(host, web, bRef):

        url = 'http://{}:{}/web/epgbouquet'.format(host, web)
        data = {'bRef': bRef}
        soup = get_data((url, data))
        results = get_events(soup)
        return results


    def get_fullepg(host, web, sRef):

        url = 'http://{}:{}/web/epgservice'.format(host, web)
        data = {'sRef': sRef}
        soup = get_data((url, data))
        results = get_events(soup)
        return results

    def get_now(host, web, sRef):

        url = 'http://{}:{}/web/epgservicenow'.format(host, web)
        data = {'sRef': sRef}
        soup = get_data((url, data))
        results = get_events(soup)
        return results


    def get_nownext(host, web, sRef):

        url = 'http://{}:{}/web/epgservicenow'.format(host, web)
        url2 = 'http://{}:{}/web/epgservicenext'.format(host, web)
        data = {'sRef': sRef}
        soup = get_data((url, data), (url2, data))
        results = get_events(soup)
        return results

    ###############################################################
    # Gets the stuff we need from the box and returns soup        #
    ###############################################################
    def get_data(*args):
        #TODO Pass in a timeout value here
        from httplib2 import Http
        from urllib import urlencode
        req = Http(timeout=10)
        results = []
        for item in args:
            u = item[0]
            data = item[1]
            print data
            try:
                if data:
                    headers = {'Content-type': 'application/x-www-form-urlencoded'}
                    resp, content = req.request(u, "POST", headers=headers, body=urlencode(data))
                    print resp, content
                else:
                    resp, content = req.request(u, "GET", data)
                soup = BeautifulSoup(content)
                results.append(soup)
            except:

                raise
        return results

if __name__ == '__main__':
    d = BouquetMonitor()
    d.process_bouquets('192.168.1.252', 80)