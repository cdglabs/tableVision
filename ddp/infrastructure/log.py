import cv2
import numpy as np
import networkx as nx
import os
import glob


# TODO: output as live cv2 tiled images



_out_method = "file"
_out_count = 0
_out_prefix = "out"

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
    global _out_count
    _out_count = _out_count + 1
    return "log/" + _out_prefix + str(_out_count).rjust(3, "0") + "." + file_extension





def image(background=None, width=800, height=600, contours=[], points=[], lines=[], pixels=[]):
    if background is None:
        img = np.zeros((height,width,3), np.uint8)
    elif len(background.shape) == 2:
        img = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)
    else:
        img = background.copy()

    cv2.drawContours(img, contours, -1, (0,100,255), 2)
    for (x,y) in pixels:
        img[y,x] = [100,0,255]
    for (p1, p2) in lines:
        cv2.line(img, p1, p2, (0,255,0), 2)
    for point in points:
        cv2.circle(img, point, 4, (0,0,255), -1)

    if _out_method == "file":
        file_name = generate_file_name("png")
        cv2.imwrite(file_name, img)
    # TODO: else, cv2 window, etc.


def gpickle(graph):
    if _out_method == "file":
        file_name = generate_file_name("gpickle")
        nx.write_gpickle(graph, file_name)
