import cv2
import infrastructure.log as log
import infrastructure.intake as intake
from core import vision
import numpy as np
import core.vision as vision
import core.topology as topology
import math
import infrastructure.helper as helper

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph
from pipeline.hv_lines import run as hv_lines
from Settings import Settings


def run(img):
    # log.image(img)
    extracted = extract_paper(img, logOn=False)
    white_balanced_image = vision.white_balance(extracted)
    # log.image(white_balanced_image)
    hsv = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)
    
    # problem: normal cv2.COLOR_BGR2GRAY converts to a very light grey for, say, yellow strokes
    # grey = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2GRAY)
    # convert to grey emphasising saturation!
    hsv_factors = [0, -2, 1]
    mat = np.array(hsv_factors).reshape((1,3))
    myGrey = cv2.transform(hsv, mat)
    # log.image(myGrey)
    
    stroke_width_px_int = int( math.ceil( Settings.STROKE_WIDTH_MM * Settings.PIXELS_PER_MM ) )
    # Size of a pixel neighborhood that is used to calculate a threshold value
    blockSize = stroke_width_px_int * 25
    noise_reduction = 25
    def uneven(x): return x + x % 2 + 1
    # http://docs.opencv.org/2.4/modules/imgproc/doc/miscellaneous_transformations.html
    binarized = cv2.adaptiveThreshold(
        myGrey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        uneven(blockSize), noise_reduction
    )
    # log.image(binarized)
    
    filtered = vision.remove_noise_from_binary_image(binarized)
    filtered = vision.delete_margins_from_binary_image(filtered)
    log.image(filtered)
    
    skeleton = vision.skeletonize(filtered)
    log.image(background=skeleton)
    
    graph = topology.produce_graph(skeleton, hsv_image=hsv)
    log.image(
        background=white_balanced_image,
        pixels=graph.nodes(),
        graph=graph
    )
    
    

def sample():
    return intake.image_file("input/photo004.png")
    # return intake.image_file("input/photo003_colors.png")
