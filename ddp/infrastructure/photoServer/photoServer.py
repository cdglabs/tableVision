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
        print self.address, "set message"
    
    def handleConnected(self):
        print self.address, 'connected'
        file = take_picture_from_camera()
        # file = "grid_drawing.jpg"
        with open(file, "rb") as image_file:  # 
            print "sending " + file + " to " + self.address[0]
            self.sendMessage(image_file.read())
            print "done sending"

    def handleClose(self):
        print self.address, 'closed'
