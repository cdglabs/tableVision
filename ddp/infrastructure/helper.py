import os
from sys import platform
import cv2


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


def take_picture_from_webcam():
    cap = cv2.VideoCapture(1)
    
    # take 3, because the first couple may be screwed
    ret, frame = cap.read()
    ret, frame = cap.read()
    ret, frame = cap.read()
    
    print "saving to: "+get_free_filename()
    cv2.imwrite(get_free_filename(), frame)
    
    cap.release()
    cv2.destroyAllWindows()
