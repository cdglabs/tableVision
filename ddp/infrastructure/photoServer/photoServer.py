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


class TakePhotoServer(WebSocket):
    def handleMessage(self):
        with open(take_picture_from_camera(), "rb") as image_file:
            self.sendMessage(image_file.read())
    
    def handleConnected(self):
        pass
    
    def handleClose(self):
        pass
