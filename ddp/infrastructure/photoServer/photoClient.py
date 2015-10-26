# sudo pip install websocket-client
from websocket import create_connection
import os


def get_free_filename():
    filename_number = 1
    get_filename = lambda: os.getcwd()+"/"+"photo"+str(filename_number).zfill(3)+".jpg"
    while os.path.isfile(get_filename()):
        filename_number += 1
    return get_filename()


def request_file():
    ws = create_connection("ws://localhost:8000/")
    print "Sending 'Hello, World'..."
    ws.send("Hello, World")
    print "Sent"
    print "Reeiving..."
    result = ws.recv()
    print type(result)
    print len(result)
    with open(get_free_filename(), 'w') as img:
        img.write(result)
    ws.close()

request_file()
