__author__ = 'marcgreenwood'


import cherrypy

""""
class LiveManifestMonitor(cherrypy.process.plugins.Monitor):


    def __init__(self, frequency=5):

        super(LiveManifestMonitor, self).__init__(cherrypy.bus, self.update, frequency)

        # load the manifest file into memory
        self.manifest = []
        try:
            with open('manifest.m3u8', 'r') as manifestfile:
                [self.manifest.append(line) for line in manifestfile.readlines()]
                cherrypy.log(str(self.manifest))
            # TODO delete any previous live manifest files and segments
        except:
            cherrypy.log('Error opening manifest file')


    def update(self):

        live_manifest = []

        try:
            with open('live_manifest.m3u8', 'r') as live_manifestfile:
                # load all the segment times in the live file
                [live_manifest.append(line) for line in live_manifestfile.readlines() if '#EXTINF:' in line]
            cherrypy.log(str(live_manifest))
            self.update_manifest(live_manifest)
            # TODO delete any previous live manifest files and segments
        except:
            cherrypy.log('Error opening live manifest file')


    def update_manifest(self, live_manifest):

        Creates a new manifest file
        :n:

        new_manifest = []
        for line in self.manifest:

            if '#EXTINF:' in line:
                try:
                    new_manifest.append(live_manifest.pop(0))
                except:
                    #no live data yet
                    new_manifest.append(line)
            elif 'CACHE' in line:
                # set the cache mode to No
                new_manifest.append('#EXT-X-ALLOW-CACHE:NO')
            else:
                new_manifest.append(line)

        return new_manifest

    def write_manifest(self, new_manifest):

        Writes the updated file to disk
        :param new_manifest:
        :return:

        try:

        """


class Home():

    def checkRequest(self):

        if cherrypy.request.path_info:
            import time
            time.sleep(12)
            cherrypy.log('request manifest. Sleeping')

    def checkResponse(self):

        if cherrypy.response.status == '404':
            import time
            time.sleep(10)
            cherrypy.log('Sleeping')


    cherrypy.tools.checkrequest = cherrypy.Tool('on_start_resource', checkRequest)
    cherrypy.tools.checkresponse = cherrypy.Tool('on_start_resource', checkResponse)



cherrypy.quickstart(Home(), config='config.conf')