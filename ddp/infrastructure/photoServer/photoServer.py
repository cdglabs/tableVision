import os
from sys import platform
from SimpleWebSocketServer import WebSocket


def get_free_filename():
    filename_number = 1
    get_filename = lambda: os.getcwd()+"/"+"photo"+str(filename_number).zfill(3)+".jpg"
    while os.path.isfile(get_filename()):
        filename_number += 1
    return get_filename()


def take_picture_from_camera():
    file = get_free_filename()
    print "trying to capture: " + file
    if platform == "darwin":  # on MAC, kill processes that take possession of camera
        os.system("killall PTPCamera")
    os.system("gphoto2 --capture-image-and-download --filename=" + file)
    assert os.path.isfile(file)
    return file


clients = []
class TakePhotoServer(WebSocket):
    def handleMessage(self):
        with open(take_picture_from_camera(), "rb") as image_file:
            for client in list(clients):
                if client != self:
                    client.sendMessage(self.address[0] + ' - ' + image_file.read())
                    print "sending " + image_file + " to " + self.address[0]
    
    def handleConnected(self):
        print self.address, 'connected'
        for client in list(clients):
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        print self.address, 'closed'
        for client in list(clients):
            client.sendMessage(self.address[0] + u' - disconnected')