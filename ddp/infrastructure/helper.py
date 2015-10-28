import os
from sys import platform
import cv2

_default_cam_no = 0

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


def get_webcam_capture(camNo=_default_cam_no):
    cap = cv2.VideoCapture(camNo)
    # resolution
    cap.set(3, 2592)
    cap.set(4, 1944)
    return cap


def take_picture_from_webcam(camNo=_default_cam_no):
    cap = get_webcam_capture(camNo)
    # take 3, because the first couple may be screwed
    cap.read()
    cap.read()
    ret, frame = cap.read()
    file = save_frame(frame)
    cap.release()
    return file


def save_frame(frame):
    file = get_free_filename()
    cv2.imwrite(file, frame)
    return file
