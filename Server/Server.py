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

class InternalRedirector(object):

    """WSGI middleware that handles raised cherrypy.InternalRedirect."""

    def __init__(self, nextapp, recursive=False):
        self.nextapp = nextapp
        self.recursive = recursive

    def __call__(self, environ, start_response):
        redirections = []
        while True:
            environ = environ.copy()
            try:
                return self.nextapp(environ, start_response)
            except _cherrypy.InternalRedirect:
                ir = _sys.exc_info()[1]
                sn = environ.get('SCRIPT_NAME', '')
                path = environ.get('PATH_INFO', '')
                qs = environ.get('QUERY_STRING', '')

                # Add the *previous* path_info + qs to redirections.
                old_uri = sn + path
                if qs:
                    old_uri += "?" + qs
                redirections.append(old_uri)

                if not self.recursive:
                    # Check to see if the new URI has been redirected to
                    # already
                    new_uri = sn + ir.path
                    if ir.query_string:
                        new_uri += "?" + ir.query_string
                    if new_uri in redirections:
                        ir.request.close()
                        raise RuntimeError("InternalRedirector visited the "
                                           "same URL twice: %r" % new_uri)

                # Munge the environment and try again.
                environ['REQUEST_METHOD'] = "GET"
                environ['PATH_INFO'] = ir.path
                environ['QUERY_STRING'] = ir.query_string
                environ['wsgi.input'] = BytesIO()
                environ['CONTENT_LENGTH'] = "0"
                environ['cherrypy.previous_request'] = ir.request


class Home():



    def checkRequest():
        if cherrypy.request.prev is not None:
            cherrypy.log(str(cherrypy.request.prev))

        if 'manifest.m3u8' in cherrypy.request.path_info:
            import time
            cherrypy.log('request manifest. Sleeping')
            time.sleep(9.5) # 10 SECONDS SEEMS TO BE TOO LONG. GIVES A PLAYBACK ERROR ON ANDROID


    def checkResponse():
        if cherrypy.response.status == 404:



            raise cherrypy.HTTPRedirect(cherrypy.request.path_info)




    cherrypy.tools.checkrequest = cherrypy.Tool('on_start_resource', checkRequest)
    cherrypy.tools.checkresponse = cherrypy.Tool('before_finalize', checkResponse)



cherrypy.quickstart(Home(), config='config.conf')
"""
ffmpeg -i http://192.168.1.252:8001/1:0:1:1933:7FF:2:11A0000:0:0:0: -b:v 128k -force_key_frames 2  -f segment -segment_list_flags +live -segment_list live_manifest.m3u8 -segment_time 2 out%03d.ts
"""