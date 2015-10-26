import signal
import sys
import ssl
from optparse import OptionParser

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
import helper


class TakePhotoServer(WebSocket):
    def handleMessage(self):
        print self.address, "sent message"
    
    def handleConnected(self):
        print self.address, 'connected'
        file = helper.take_picture_from_camera()
        # file = "grid_drawing.jpg"
        with open(file, "rb") as image_file:  # 
            print "sending " + file + " to " + self.address[0]
            self.sendMessage(image_file.read())
            print "done sending"

    def handleClose(self):
        print self.address, 'closed'


if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
    # parser.add_option("--example", default='', type='string', action="store", dest="example", help="echo, chat")
    parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
    parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
    parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
    
    (options, args) = parser.parse_args()
    
    cls = TakePhotoServer
    
    if options.ssl == 1:
        server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
    else:
        server = SimpleWebSocketServer(options.host, options.port, cls)
    
    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()
    
    signal.signal(signal.SIGINT, close_sig_handler)
    
    server.serveforever()
