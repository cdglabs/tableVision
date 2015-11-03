import os
from sys import platform
import cv2
import numpy as np
from Settings import Settings


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


def get_webcam_capture(camNo=Settings.DEFAULT_CAM_NO):
    cap = cv2.VideoCapture(camNo)
    # resolution
    cap.set(3, 2592)
    cap.set(4, 1944)
    return cap


def take_picture_from_webcam(camNo=Settings.DEFAULT_CAM_NO):
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


class Colors:
    # easy to segment colours
    Black = 0
    Red = 1
    Yellow = 2
    Green = 3
    Blue_aqua = 4
    Violett = 5
    
    @staticmethod
    def rgb2hsv((r,g,b)):
        return Colors.convert_color([r,g,b], cv2.COLOR_RGB2HSV)
        
    @staticmethod
    def hsv2rgb((h,s,v)):
        return Colors.convert_color([h,s,v], cv2.COLOR_HSV2RGB)
    
    # slow? perhaps use import colorsys instead?
    @staticmethod
    def convert_color(color, cv2flag):
        return tuple(cv2.cvtColor(np.uint8([[color]]), cv2flag)[0][0])
    
    @staticmethod
    def get_rgb(color):
        return Colors.hsv2rgb(Colors.get_hsv(color))
    
    @staticmethod
    def get_hsv(color):
        if color == Colors.Black: return 0, 0, 255  # white for debugging
        if color == Colors.Red: return 0, 255, 255
        if color == Colors.Yellow: return 30, 255, 255
        if color == Colors.Green: return 60, 255, 255
        if color == Colors.Blue_aqua: return 90, 255, 255
        if color == Colors.Violett: return 150, 255, 255
        assert False, "fell through"

    @staticmethod
    def get_color_compartment((hue, sat, value)):
        def inn(x, low, high):
            return low <= x and x < high
        
        # theoretical color centers:
        # {'red': 0, 'yellow': 30, 'green': 60, 'aqua': 90, 'blue': 120, 'violett': 150}
        assert inn(hue, 0, 180)
        assert inn(sat, 0, 256)
        assert inn(value, 0, 256)
        
        if sat < 30 or value < 100:
            return Colors.Black
        
        # empirically determined
        if inn(hue, 0, 17) or inn(hue, 153, 180):
            return Colors.Red
        if inn(hue, 17, 35):
            return Colors.Yellow
        if inn(hue, 35, 84):
            return Colors.Green
        if inn(hue, 84, 115):
            return Colors.Blue_aqua
        if inn(hue, 115, 153):
            return Colors.Violett
        
        assert False, "fell through"
    