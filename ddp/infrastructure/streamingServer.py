import signal
import sys
import ssl
from optparse import OptionParser
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
import helper
import StringIO
import numpy as np

# more info: https://github.com/dpallot/simple-websocket-server/blob/master/SimpleWebSocketServer/SimpleExampleServer.py

class StreamingServer(WebSocket):
    clients = []
    capture = helper.get_webcam_capture()
    
    def sendFrame(self):
        print self.address, 'serving frame.'
        _, frame = self.capture.read()
        # frame is a numpy array. serialise frame into memory and send.
        memfile = StringIO.StringIO()
        np.save(memfile, frame)
        memfile.seek(0)
        self.sendMessage(memfile.read())
    
    def handleMessage(self):
        if self.data == "get frame":
            self.sendFrame()
    
    def handleConnected(self):
        self.clients.append(self)
        print self.address, 'connected'

    def handleClose(self):
        self.clients.remove(self)
        print self.address, 'closed'


if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")

    (options, args) = parser.parse_args()
    cls = StreamingServer
    server = SimpleWebSocketServer(options.host, options.port, cls)
    
    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()
    
    signal.signal(signal.SIGINT, close_sig_handler)
    server.serveforever()
