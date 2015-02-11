import time
from PluginBase import PluginBase, MessageResponse
from StringIO import StringIO
import cherrypy
import subprocess




class Transcoder(PluginBase):

    def __init__(self, bus):
        super(Transcoder, self).__init__(bus, name='transcoder')
        self.started = False
        self.process = None
        self.action_dict.update({'start_transcoder': Transcoder.startFFMPEG,
                                 'stop_transcoder': Transcoder.stopFFMPEG})

    def start(self):
        self.bus.log('Starting transcoder plugin')

    def stop(self):
        self.bus.log('Stoppping transcoder plugin')
        self.bus.unsubscribe('ffmpeg', self.dispatch)
        if self.process is not None:
            self.process.kill()
            self.process = None
            self.bus.log('Stoppped ffmmpeg')

    def startFFMPEG(self, data):
        cherrypy.log('Starting FFMPEG')

        params= {
            '-override_ffserver': '',
            '-map': ('0:0', '0:1'),
            '-s': '1920x1080',
            '-buffer_size': '10240000',
            '-vcodec': 'libx264',
            '-preset': 'ultrafast',
            '-strict': 'experimental',
            '-vf': 'yadif',
            '-acodec': 'libfaac',
            '-ab': '96000',
            '-ac': '2',

        }
        '''
        http://192.168.1.252:8001/1:0:1:272E:801:2:11A0000:0:0:0: -
        http://192.168.1.100:28090/audio1.ffm
        '''

        script, action, data = data
        self.process = subprocess.Popen(['ffmpeg', '-i', 'http://192.168.1.252:8001/1:0:1:272E:801:2:11A0000:0:0:0:',
                                         '-override_ffserver',
                                         '-map', params['-map'][0],
                                         '-map', params['-map'][1],
                                         '-s', params['-s'],
                                         '-buffer_size', params['-buffer_size'],
                                         '-vcodec', params['-vcodec'],
                                         '-preset', params['-preset'],
                                         '-strict', params['-strict'],
                                         '-vf', params['-vf'],
                                         '-acodec', params['-acodec'],
                                         '-ab', params['-ab'],
                                         '-ac', params['-ac'],
                                         'http://192.168.1.100:28090/audio1.ffm'

                                         ],
                                            bufsize=96,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=True)
        line = self.process.stdout.readline()
        self.bus.log(line)
        while 'frame=' not in line:
            line = self.process.stdout.readline()
            self.bus.log(line)
            self.process.stdout.flush()


        response = MessageResponse(1, script, action, '1')
        cherrypy.engine.publish(script, response)
        self.bus.log('started ffmpeg')
        #todo may need to remove ffm file frmo tmp when stopping. - Yes I think
        #todo Need to monitor Plex Media Server.log to look for cleanup signal when video stream is closed

    def stopFFMPEG(self, data):
        self.bus.log('Stoppping ffmmpeg')
        if self.process is not None:
            self.process.kill()
            self.process = None



