__author__ = 'marcgreenwood'


import cherrypy
from cherrypy.lib.static import serve_file



class Home():



    @cherrypy.expose
    def index(self):
        import os
        return serve_file(os.path.abspath('.') + '/html/index.html')



cherrypy.quickstart(Home(), config='config.conf')
"""
ffmpeg -i http://192.168.1.252:8001/1:0:1:1933:7FF:2:11A0000:0:0:0: -b:v 128k -force_key_frames 2  -f segment -segment_list_flags +live -segment_list live_manifest.m3u8 -segment_time 2 out%03d.ts
"""