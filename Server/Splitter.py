

__author__ = 'Marc Greenwood'

from Base.Component import Component, Segment
from multiprocessing import Process
import urllib2
import cherrypy
from bitstring import BitArray, BitString


class Splitter(Component):

    """
    Constructor passes itself to superclass. This is then passed to cherrypy as the Root() :)
    """
    def __init__(self, address=None, authkey=None):
        #Thi switch is due to the proxy being created at the other end,
        #otherwise we re-open cherrypy on the other client and things get messy
        if address is None and authkey is None:
            #new instance
            super(Splitter, self).__init__(root=self, address=None, authkey=None, config="splitter.config")
            cherrypy.server.socket_port = cherrypy.request.app.config['component_params']['my_port']
        else:
            #pass None though for root as we've already initialised
            #pass  address, authkey through so the client knows how to contact us when using the proxy
            super(Splitter, self).__init__(root=None, address=address, authkey=authkey)

        self.id = 0


    """
    Overrides default start_component. Adds a file writer to the default functionality
    so transcoded segments can be written to disk. Segments will be put on the queue by one or more transcoders
    """
    def start_component(self):

        # I will need to move these at some point as they willonly need starting when th
        #user presses the connect button
        Process(target=self.packetise, args=(self.receive_queue, )).start()
        Process(target=self.create_segments, args=(self.receive_queue, self.send_queue, )).start()
        Process(target=self.send, args=(self.send_queue,)).start()
        self.start()
        self.receive_queue.join()

    def packetise(self, receive_queue=None):

        receive_queue = receive_queue
        stream_url = "http://192.168.1.252:8001/1:0:1:50DC:80F:2:11A0000:0:0:0:"
        bytes_to_read = 188

        self.log.warning("Packetiser Started")
        stream = urllib2.urlopen(stream_url)
        while 1:
            packet = stream.read(bytes_to_read)
            packet_array = BitArray(bytes=packet)
            if not packet_array.startswith('0x47'):
                print 'no sync byte found'
                break
            receive_queue.put(packet)

    def create_segments(self, receive_queue=None, send_queue=None):

        receive_queue = receive_queue
        send_queue = send_queue
        self.log.warning(receive_queue.qsize())
        audioPID, read_buffer = self.locate_audio_pid(receive_queue)
        segment_data = self.create_segment_data(receive_queue, send_queue, audioPID, read_buffer)
        self.create_segment(segment_data, send_queue)





    """
    Need the audio PID for some reason

    """
    def locate_audio_pid(self, receive_queue=None):

        audioPID = None
        read_buffer = []
        while audioPID is None:

            packet = receive_queue.get()
            packet_array = BitArray(bytes=packet)

            # get audio and video pid
            if BitString(bin=packet_array.bin[32:56]).uint == 1 and \
                    BitString(bin=packet_array.bin[56:64]).uint == 192 \
                    and audioPID is None:
                audioPID = BitString(bin=packet_array.bin[11:24]).uint
            #Save the packet
        read_buffer.append(packet)
        return audioPID, read_buffer

    def create_segment_data(self, receive_queue=None, send_queue=None, audioPID=None, read_buffer=None):

        #These are just a counter at present to
        #determine when we split the segment
        no_i_frame_found = 0
        # Temp lists to hold packets when looking for complete
        # audio frame after split
        while 1:
            packet = receive_queue.get()
            packet_array = BitArray(bytes=packet)
            #Check for adaptation field in current packet - May contain I frame
            if BitString(bin=packet_array.bin[26:28]).uint > 1:
                # Now look for the I Frame at this position. Is this the RAP ?
                if BitString(bin=packet_array.bin[41:42]).uint == 1:
                    #so why don't I count the I Frame found instead?
                    no_i_frame_found += 1
                    #Split at 12th I frame
                    if no_i_frame_found == 12:
                        self.log.warning("Enough packets to create a segment")
                        #Save the present I frame as It will start the next segment
                         # saved split point. Have to find rest of audio packets now to complete the audio frame
                        segment_data, temp_other = self.complete_audio_frame(receive_queue, send_queue, read_buffer, audioPID, packet)
                        self.create_segment(segment_data, send_queue)
                        read_buffer = self.start_new_segment_data(temp_other)
                        no_i_frame_found = 0
                    else:
                        read_buffer.append(packet)
                else:
                    read_buffer.append(packet)
            else:
                read_buffer.append(packet)

    """
    Helper methods from here onwards
    """
    def complete_audio_frame(self, receive_queue=None, send_queue=None, read_buffer=None, audioPID=None, packet=None):

        tempAudio = []
        tempOther = []
        packet = packet
        tempOther.append(packet)
        audio_counter = 0

        packet = receive_queue.get()
        packet_array = BitArray(bytes=packet)

        while 0 == (BitString(bin=packet_array.bin[56:64]).uint == 192
                and BitString(bin=packet_array.bin[11:24]).uint == audioPID
                and audio_counter):

            #Check if we have part of the audio frame in the current packet.
            # If so, save it. Check against Audio PID saved earlier
            if BitString(bin=packet_array.bin[11:24]).uint == audioPID:
                tempAudio.append(packet)
                audio_counter += 1
            #otherwise we have found a packet belonging to something else
            else:
                tempOther.append(packet)
            packet = receive_queue.get()
            packet_array = BitArray(bytes=packet)
        # this is required
        self.log.warning("complete audio frame")
        read_buffer.extend(tempAudio)
        tempOther.append(packet)
        return read_buffer, tempOther

    def create_segment(self, segment_data=None, send_queue=None):

        s = Segment(self.id, b"".join(segment_data))
        send_queue.put(s)
        self.id += 1

    def start_new_segment_data(self, tempOther=None):

        read_buffer = []
        read_buffer.extend(tempOther)
        return read_buffer









