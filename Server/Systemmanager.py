import ast
import time

__author__ = 'Marc Greenwood'

from Base.Component import Component
from multiprocessing import Process
import cherrypy
import urllib2
import json


def load_known_transcoders():
    #new dictionary to store info as tuple
    ret = {}
    transcoders = cherrypy.request.app.config['transcoders']
    for k, v in transcoders.iteritems():
            tup = ast.literal_eval(v)
            ret[(tup[0], tup[1])] = (tup[2], tup[3])
    print ret
    return ret


class SystemManager(Component):

    """
    Constructor passes itself to superclass. This is then passed to cherrypy as the Root() :)
    """
    def __init__(self, address=None, authkey=None):
        #Thi switch is due to the proxy being created at the other end,
        #otherwise we re-open cherrypy on the other client and things get messy
        if address is None and authkey is None:
            #new instance
            super(SystemManager, self).__init__(root=self, address=None, authkey=None, config="system_manager.config")
        else:
            #pass None though for root as we've already initialised
            #pass  address, authkey through so the client knows how to contact us when using the proxy
            super(SystemManager, self).__init__(root=None, address=address, authkey=authkey)

        #Initialise system manager specific option
        #dictionary of transcoders
        self.transcoder_queue = {}
        #dictionary to store busy transcoders
        self.transcoder_busy = {}
        #dictionar of other components
        self.components = {}
        self.trans_receive_queue = None
        self.server_receive_queue = None


        self.transcoder_queue = load_known_transcoders()

        self.start_component()



    """
    Overrides default start_component. Adds a file writer to the default functionality
    so transcoded segments can be written to disk. Segments will be put on the queue by one or more transcoders
    """
    def start_component(self):
        #Just start my queue manager
        self.start()
        #Start process to find other components and start them up
        Process(target=self.do_something, args=(self.receive_queue, self.send_queue)).start()
        # Start a process to send segements to correct transcoder when required

    def do_something(self, receive_queue=None, send_queue=None):

        receive_queue = receive_queue
        send_queue = send_queue

        self.log.info("Scanning for components")
        #The system manager needs to find everything it needs and start them
        found_components = self.scanner()
        self.start_server(found_components)
        self.process_transcoders(found_components)
        self.start_splitter(found_components)
        Process(target=self.send, args=(self.send_queue, self.trans_receive_queue, self.server_receive_queue)).start()
        while 1:
            send_queue.put(receive_queue.get())
            receive_queue.task_done()
            self.log.info("System Manager  processing segment")

    def scanner(self):

        components_found = []

        ip = self.get_my_ip()

        for i in range (1, 255):
            iplist = ip.split(".")
            iplist[3] = i
            address = "{}.{}.{}.{}".format(iplist[0], iplist[1],iplist[2],iplist[3])
            self.log.info('Searching {}'.format(address))
            for port in range(33540, 33580, 10):
                try:
                    res = urllib2.urlopen('http://{}:{}/identify'.format(address, port), timeout=0.030)
                    if res.code == 200:
                        j = res.read()
                        type = json.loads(j)['type']
                        data_port = json.loads(j)['my_data_port']
                        self.log.info("***** Found a {} . It's data port is {} *****".format(type, data_port))
                        components_found.append((address, type, data_port))

                #returns a tuple that we can get the error number and message from. Activley refused is 10061.
                #timeout is just a timeout error
                except Exception as e:
                    pass
        return components_found

    def get_my_ip(self):

        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def send(self, send_queue=None, trans_receive_queue=None, server_receive_queue=None):

        while 1:
            segment = send_queue.get()
            if segment.is_transcoded:
                server_receive_queue.put(segment)
                self.log.info("sent segment to server")
            else:
                # TODO Do some logic here to determine which transcoder to send to atm we just have one so create temp variable
                trans_receive_queue.put(segment)
                self.log.info("sent segment to transcoder")
            send_queue.task_done()


    def start_server(self, found_components=None):

        for ip, type, port in [x for x in found_components if x[1] == 'Server']:

            # it would be good to make these tuples match the ones we got when we found it
            #as we are using it as a key in the dict
            #setup connections and connect code here
            res = urllib2.urlopen('http://{}:{}/startcomponent'.format(ip, 33560), timeout=0.10)
            #just give it enough time to start
            time.sleep(0.5)
            Component.register('receive_queue')
            component = Component(address=(ip, port), authkey="abc")
            component.connect()
            self.server_receive_queue = component.receive_queue()
            self.log.info("Connected to {}".format(type))

    def process_transcoders(self, found_components=None):
         #Filter out all the transcoders after we have found out components
        #Transcoders need to connect to here, so send details when starting up
        speed = 2
        for ip, type, port in [x for x in found_components if x[1] == 'TranscoderClient']:

            # it would be good to make these tuples match the ones we got when we found it
            #as we are using it as a key in the dict
            if (ip, type) in self.transcoder_queue:
                #setup connections and connect code here
                res = urllib2.urlopen('http://{}:{}/startcomponent'.format(ip, 33570), timeout=0.10)
                #just give it enough time to start
                time.sleep(0.5)
                Component.register('receive_queue')
                component = Component(address=(ip, port), authkey="abc")
                component.connect()
                #self.transcoder_queue[(ip, type)] = (port, component.receive_queue())
                self.log.info("Connected to {}".format(type))
                self.trans_receive_queue = component.receive_queue()
            else:
                #benchmark transcoders
                #speed = benchmark((ip, type, port))
                # then put the queue in a dict so we can put on it later
                self.transcoder_queue[(ip, type)] = (port, (speed / 5))
                speed += 1.0

    def start_splitter(self, found_components=None):

        for ip, type, port in [x for x in found_components if x[1] == 'Splitter']:

            # it would be good to make these tuples match the ones we got when we found it
            #as we are using it as a key in the dict
            #setup connections and connect code here
            res = urllib2.urlopen('http://{}:{}/startcomponent'.format(ip, 33540), timeout=0.10)
            #just give it enough time to start
            time.sleep(0.5)
            self.log.info("Started {}".format(type))


    def which_transcoder(self):

        from operator import itemgetter

        #a bit late down the line, decide which ne to put the segment on
        # do we need to mark a transcoder as free / busy somehow....
        # ave two dicts. Remove from queue and put into busy and visa versa

        #...Sorts the queue, then gets the empty ones, that are not currently busy. (The task
        # done signal may not have been received by the queue handler, even though the item
        # will be currently transcoding)
        #Need to check that there's more than one varsalue brought back as this will fail if nothing left
        # cant we just check that there not in the busy list.

        k = [[k, v] for k, v in sorted(self.transcoder_queue.iteritems(), key=itemgetter(1)) if v[1].empty() and k not in self.transcoder_busy]
        # then gets the first one thats fastest. THis just checks to make sure
        #actually have something thats empty
        if len(k) > 0:
            ip, type, port = k[0][0]
            #send segment to transcode
            print ip
            print type
            print port
        else:
            #Nothing Free :(

            print ("Nothing free")
            #check which is due to finish first
            false_duration = 5
            false_time = 200.00
            leader = None
            #need to get the ratio ere of each busy
            for k, v in busy.items():
                ratio =  self.transcoder_queue.get(k)
                if ratio:
                    # we have an entry
                    if (false_duration - (time.time() - v)) * ratio[0] < false_time:
                        leader = k
            return leader



        #print time.time()-busy[('192.168.1.2', 'TranscoderClient', 35561)]













