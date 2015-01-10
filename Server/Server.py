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

    def checkRequest():

        if 'manifest.m3u8' in cherrypy.request.path_info:
            import time
            cherrypy.log('request manifest. Sleeping')
            time.sleep(8) \ 10 SECONDS SEEMS TO BE TOO LONG. GIVES A PLAYBACK ERROR ON ANDROID


    def checkResponse():
        if cherrypy.response.status == 404:
            import time
            cherrypy.log('Sleeping for segment')
            # TODO DOes this have to sleep long enought so a few segments are created 3 x 2 = 6 seconds Seems to crash if it does too many 404s in an amount of time, not in a row
            # TODO seems to work, added another second . Creates another 3 after a 404 without the one. MAY NNED ONE ON TO GIV E IT VHANCE TO VATCH UP. STUTTERED A BIT WHEN IT RAN OUT OF SEGMENTS
            time.sleep(7)
            #todo do a redirect of the original request



    cherrypy.tools.checkrequest = cherrypy.Tool('on_start_resource', checkRequest)
    cherrypy.tools.checkresponse = cherrypy.Tool('before_finalize', checkResponse)



cherrypy.quickstart(Home(), config='config.conf')