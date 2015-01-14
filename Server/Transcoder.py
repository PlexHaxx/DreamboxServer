

__author__ = 'Marc Greenwood'

from Base.Component import Component
from multiprocessing import Process
from datetime import datetime
import time


class TranscoderClient(Component):

    """
    Constructor passes itself to superclass. This is then passed to cherrypy as the Root() :)
    """
    def __init__(self, address=None, authkey=None):
        #Thi switch is due to the proxy being created at the other end,
        #otherwise we re-open cherrypy on the other client and things get messy
        if address is None and authkey is None:
            #new instance
            super(TranscoderClient, self).__init__(root=self, address=None, authkey=None,config="transcoder.config")
            #set variables
            self.bitrate = 20000
            self.width = 512
            self.height = 288
        else:
            #pass None though for root as we've already initialised
            #pass  address, authkey through so the client knows how to contact us when using the proxy
            super(TranscoderClient, self).__init__(root=None, address=address, authkey=authkey)

    """
    Overrides default start_component. Adds a file writer to the default functionality
    so transcoded segments can be written to disk. Segments will be put on the queue by one or more transcoders
    """
    def start_component(self):
        # I will need to move these at some point as they will only need starting when th
        #user presses the connect button
        Process(target=self.transcode, args=(self.receive_queue, self.send_queue)).start()
        Process(target=self.send, args=(self.send_queue,)).start()
        self.start()
        self.receive_queue.join()


    """
    transcodes a segment when it is placed on the queue
    """

    def transcode(self, receive_queue=None, send_queue=None, bitrate=400000, width=1024, height=572):

        bitrate = str(bitrate)
        size = 'scale={}:{}'.format(width, height)
        receive_queue = receive_queue
        send_queue = send_queue

        import subprocess

        while 1:
            self.log.info("Transcoder waiting for segment")
            segment = receive_queue.get()
            segment_id = segment.segment_id
            segment_data = segment.segment_data
            self.log.info(" Transcoder received segment {} ".format( segment_id))
            handle = subprocess.Popen(['ffmpeg', '-i', '-', '-vf', size, '-b:v', bitrate, '-f', 'mpegts', '-'],
                                      bufsize=4096, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

            transcoded_data = handle.communicate(segment_data)[0]
            self.log.info("Transcoder finished transcode of segment {} ".format(segment_id))
            segment.segment_data = transcoded_data
            segment.is_transcoded = True
            send_queue.put(segment)
            receive_queue.task_done()







