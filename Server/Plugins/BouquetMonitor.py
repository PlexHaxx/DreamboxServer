

import pycurl
from StringIO import StringIO
from urllib import urlencode

import cherrypy

class BouquetMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self):

        super(BouquetMonitor, self).__init__(cherrypy.engine, None, )
        self.host = '192.168.1.252'
        self.port = 80

        self.frequency= 60
        self.callback = self.monitor


    def monitor(self):
        self.get_bouquets(self.host, self.port)


    def get_bouquets(self, host, port):

        url = 'http://{}:{}/web/getservices'.format(host, port)
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        print buffer.getvalue()
        return buffer.getvalue()



    def get_current_service(host, web):

        url = 'http://{}:{}/web/getcurrent'.format(host, web)
        try:
            soup = get_data((url, None))
            results = get_current_service_info(soup)
        except:
            raise
        return results

    def get_channels_from_service(self, host, web, sRef=None, show_epg=False):

        url = 'http://{}:{}/web/getservices'.format(host, web)
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        post_data = {'sRef': '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.enterainment__tv_.tv"'}
        # Form data must be provided already urlencoded.
        postfields = urlencode(post_data)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        c.setopt(c.POSTFIELDS, postfields)
        c.perform()
        c.close()
        print buffer.getvalue()
        return buffer

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
    d.get_bouquets('192.168.1.252', 80)