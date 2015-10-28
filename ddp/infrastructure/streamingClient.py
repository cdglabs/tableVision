# sudo pip install websocket-client
import websocket
import time
import threading
import StringIO
import numpy as np
import cv2
import helper

_default_ip = "192.168.1.155"
_default_port = "8000"

waitForResponseEvent = threading.Event()
waitForWebsocketToOpen = threading.Event()
received_image = None


def on_message(ws, result):
    global received_image
    # print "receiving message", type(result), len(result)#, result
    memfile = StringIO.StringIO()
    memfile.write(result)
    memfile.seek(0)
    frame = np.load(memfile)
    received_image = frame
    waitForResponseEvent.set()


def on_close(ws, message):
    print "on_close", message
    ws.close()

def on_error(ws, message):
    print "error in websocket.", message
    ws.close()


def on_open(ws):
    # print "websocket client running..."
    waitForWebsocketToOpen.set()


class ClientThread(threading.Thread):
    def __init__(self, ip, port):
        # print "thread: init"
        threading.Thread.__init__(self)
        self.ws = websocket.WebSocketApp("ws://" + ip + ":" + port + "/",
            on_message = on_message,  # for some reason, those can not be class methods
            on_error = on_error,
            on_close = on_close,
            on_open = on_open)
    
    def run(self):
        # print "thread: run"
        self.ws.run_forever()
        # print "thread: exiting"
    
    def release(self):
        self.ws.close()
    
    # this is designed to look like cv2.VideoCapture.read()
    def read(self):
        # print "thread: get frame"
        self.ws.send("get frame")
        waitForResponseEvent.wait()
        waitForResponseEvent.clear()
        assert received_image is not None
        return True, received_image


def connect_to_streaming_server(ip=_default_ip, port=_default_port):
    client = ClientThread(ip, port)
    client.start()
    waitForWebsocketToOpen.wait()
    return client


def get_one_picture_from_streaming_server(ip=_default_ip, port=_default_port):
    client = connect_to_streaming_server(ip, port)
    _, frame = client.read()
    client.release()
    client.join()
    return frame


if __name__ == "__main__":
    frame = get_one_picture_from_streaming_server()
    helper.save_frame(frame)
