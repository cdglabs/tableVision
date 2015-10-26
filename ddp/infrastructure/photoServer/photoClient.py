# sudo pip install websocket-client
import websocket
import os


def get_free_filename():
    filename_number = 1
    get_filename = lambda: os.getcwd()+"/"+"photo"+str(filename_number).zfill(3)+".jpg"
    while os.path.isfile(get_filename()):
        filename_number += 1
    return get_filename()


# def request_file():
#     ws = create_connection("ws://192.168.1.155:8000/")
#     # ws = create_connection("ws://localhost:8000/")
#     print "Sending 'Hello, World'..."
#     ws.send("Hello, World")
#     print "Sent"
#     print "Reeiving..."
#     result = ws.recv()
#     # print result
#     print type(result)
#     print len(result)
#     with open(get_free_filename(), 'w') as img:
#         img.write(result)
#     ws.close()
    
    
def on_message(ws, result):
    print "on_message"
    print type(result)
    print len(result)
    with open(get_free_filename(), 'w') as img:
        img.write(result)
    # print result
    
    
def on_error(ws, message):
    print "on_error"
    print message
    
    
def on_open(ws, message):
    ws.send("Hello, World")
    print "on_open"
    print message
    
    
def on_close(ws, message):
    print "on_close"
    print message
    
    
def better():
    # ws = websocket.WebSocketApp("ws://192.168.1.155:8000/",
    ws = websocket.WebSocketApp("ws://localhost:8000/",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
    ws.on_open = on_open
    
    ws.run_forever()

better()
# request_file()
