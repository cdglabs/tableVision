import os
from sys import platform
import cv2


def get_free_filename(ext="jpg"):
    dir = os.getcwd()
    assert os.path.isdir(dir)
    if os.path.isdir(dir+"/input"):
        dir += "/input"
    
    filename_number = 1
    get_filename = lambda: dir + "/photo" + str(filename_number).zfill(3) + "." + ext
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


def take_picture_from_webcam(camNo=1):
    cap = cv2.VideoCapture(camNo)
    
    # take 3, because the first couple may be screwed
    ret, frame = cap.read()
    ret, frame = cap.read()
    ret, frame = cap.read()
    
    file = get_free_filename()
    print "saving to: "+file
    cv2.imwrite(file, frame)
    
    cap.release()
    cv2.destroyAllWindows()
    return file
