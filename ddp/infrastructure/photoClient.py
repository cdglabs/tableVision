# sudo pip install websocket-client
import websocket

import helper

received_image = None


def on_message(ws, result):
    global received_image
    # print "receiving message", type(result), len(result)
    received_image = helper.get_free_filename()
    with open(received_image, 'w') as img:
        img.write(result)
    ws.close()
    
    
def on_error(ws, message):
    print "error. is the camera active?", message
    ws.close()
    
    
def on_open(ws, message):
    print "on_open", message
    
    
def on_close(ws, message):
    print "on_close", message
    

def get_photo_from_server(ip="192.168.1.155", port="8000"):
    ws = websocket.WebSocketApp("ws://"+ip+":"+port+"/",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
    if received_image is None:
        raise Exception('error')
    return received_image


if __name__ == "__main__":
    get_photo_from_server()
