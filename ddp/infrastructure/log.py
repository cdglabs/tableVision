import cv2
import numpy as np
import networkx as nx
import os
import glob
import math
import infrastructure.helper as helper
from infrastructure.helper import Colors as Colors
import time
import datetime


_out_method = "silent"
_out_count = 0
_out_prefix = "out"
_windows = []
_log_base_dir = "log/"
_log_dir_instance = None

def to_int(x):
    if hasattr(x, '__iter__'):
        return tuple(map(int, x))
    else:
        return int(x)


def bgrOrGreyImage(bgrOrGrey):
    global _out_count, _log_base_dir, _log_dir_instance
    if _out_method == "silent":
        return
    if _out_method == "file":
        if _log_dir_instance is None:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
            _log_dir_instance = _log_base_dir + st + "/"
            if not os.path.exists(_log_dir_instance):
                os.makedirs(_log_dir_instance)
        file_name = generate_file_name("png")
        # expects BGR color space, or Grey
        cv2.imwrite(file_name, bgrOrGrey)
    if _out_method == "stream":
        draw_window(bgrOrGrey)
    
    _out_count += 1


def hsvOrGreyImage(img, contours=[], points=[], lines=[], pixels=[], circles=[], graph=None):
    global _out_count, _log_base_dir, _log_dir_instance
    if _out_method == "silent":
        return
    img = img.copy()
    if len(img.shape) == 2:  # is grey
        img = helper.grey2hsv(img)
        
    cv2.drawContours(img, contours, -1, Colors.get_hsv(Colors.Red), 2)
    for (p1, p2) in lines:
        color = Colors.get_color_from_edge_in_hsv(graph, (p1, p2))
        cv2.line(img, to_int(p1), to_int(p2), to_int(color), 2)
    for point in pixels:
        (x, y) = point
        color = Colors.get_color_from_node_in_hsv(graph, point)
        img[to_int(y), to_int(x)] = to_int(color)
    for point in points:
        color = Colors.get_color_from_node_in_hsv(graph, point)
        cv2.circle(img, to_int(point), 3, to_int(color), -1)  # -1 = fill
    for (center, radius) in circles:
        cv2.circle(img, to_int(center), to_int(radius), to_int((0,255,255)), 2)
    
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    bgrOrGreyImage(img)


def draw_window(img):
    global _out_count
    assert _out_count < 64, "too many windows"
    
    window_name = str(_out_count)
    if len(_windows) <= _out_count:
        _windows.append("is_new_window")
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # expects BGR color space, or Grey
    cv2.imshow(window_name, img)


def set_method(method):
    global _out_method
    _out_method = method


def set_file_prefix(file_prefix):
    global _out_prefix
    _out_prefix = file_prefix


def clear_log_directory():
    global _log_base_dir
    files = glob.glob(_log_base_dir + "*")
    for f in files:
        os.remove(f)


def generate_file_name(file_extension):
    global _log_dir_instance
    return _log_dir_instance + _out_prefix + str(_out_count).rjust(3, "0") + "." + file_extension


def finish_log_cycle():
    global _out_count
    _out_count = 0
    # do window tiling
    # allows users to customise window size and position if no new windows where added
    if "is_new_window" in _windows:
        size = len(_windows)
        matrix_dim = int(math.ceil(math.sqrt(size)))
        total_width = 1920
        total_height = 1080
        win_width = total_width/matrix_dim
        win_height = total_height/matrix_dim

        for i in range(size):
            window_name = str(i)
            _windows[i] = None
            x = i % matrix_dim
            y = i / matrix_dim
            cv2.resizeWindow(window_name, win_width, win_height)
            cv2.moveWindow(window_name, x*win_width, y*win_height)


def gpickle(graph):
    if _out_method == "file":
        file_name = generate_file_name("gpickle")
        nx.write_gpickle(graph, file_name)
