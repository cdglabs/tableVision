import cv2
import numpy as np
import networkx as nx
import os
import glob
import math
import infrastructure.helper as helper


_out_method = "silent"
_out_count = 0
_out_prefix = "out"
_windows = []

def to_int(x):
    if hasattr(x, '__iter__'):
        return tuple(map(int, x))
    else:
        return int(x)


def image(background=None, width=800, height=600, # TODO width and height correct?
          contours=[], points=[], lines=[], pixels=[], circles=[], graph=None):
    global _out_count
    if _out_method == "silent":
        return
    if background is None:
        img = np.zeros((height,width,3), np.uint8)
    elif len(background.shape) == 2:
        img = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)
    else:
        img = background.copy()
    
    def get_color_from_node(node, default_color=(0,0,255)):
        if graph is not None and 'color' in graph.node[node]:
            return helper.Colors.get_rgb(graph.node[node]['color'])
        return default_color
    
    cv2.drawContours(img, contours, -1, (0,100,255), 2)
    for point in pixels:
        (x,y) = point
        (r,g,b) = get_color_from_node(point, (0,0,255))
        # BGR
        img[to_int(y),to_int(x)] = np.uint8([b,g,r])
    for (p1, p2) in lines:
        cv2.line(img, to_int(p1), to_int(p2), (0,255,0), 2)
    for point in points:
        color = get_color_from_node(point, (0,0,255))
        cv2.circle(img, to_int(point), 4, color, -1)
    for (center, radius) in circles:
        cv2.circle(img, to_int(center), to_int(radius), (0,255,0), 2)
    
    
    if _out_method == "file":
        file_name = generate_file_name("png")
        cv2.imwrite(file_name, img)
    if _out_method == "stream":
        draw_window(img)
    
    _out_count += 1

def draw_window(img):
    global _out_count
    assert _out_count < 64, "too many windows"
    
    window_name = str(_out_count)
    if len(_windows) <= _out_count:
        _windows.append("is_new_window")
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    cv2.imshow(window_name, img)


def set_method(method):
    global _out_method
    _out_method = method


def set_file_prefix(file_prefix):
    global _out_prefix
    _out_prefix = file_prefix


def clear_log_directory():
    files = glob.glob("log/*")
    for f in files:
        os.remove(f)


def generate_file_name(file_extension):
    return "log/" + _out_prefix + str(_out_count).rjust(3, "0") + "." + file_extension


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
