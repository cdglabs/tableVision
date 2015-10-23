import cv2
import networkx as nx

def image_file(file_name, gray=False):
    if gray:
        return cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    else:
        return cv2.imread(file_name, cv2.IMREAD_COLOR)

def gpickle(file_name):
    return nx.read_gpickle(file_name)

# TODO: Live webcam feed
