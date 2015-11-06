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
import core.satisfaction as satisfaction


def run(img):
    log.image(img)
    extracted = extract_paper(img, logOn=False)
    white_balanced_image = vision.white_balance(extracted)
    log.image(white_balanced_image)
    hsv = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)
    grey = vision.convert_hsv_image_to_greyscale_emphasising_saturation(hsv)
    binarized = vision.binarize_ink_IMPROVED(grey)
    log.image(binarized)
    # print white_balanced_image.shape
    
    skeleton = vision.skeletonize(binarized)
    log.image(skeleton)
    
    graph = topology.produce_graph(skeleton, hsv_image=hsv)
    log.image(
        # background=white_balanced_image,
        width=white_balanced_image.shape[1],
        height=white_balanced_image.shape[0],
        pixels=graph.nodes(),
        graph=graph
    )
    
    graph = topology.simplify_junctures(graph)
    log.image(
        width=white_balanced_image.shape[1],
        height=white_balanced_image.shape[0],
        pixels=graph.nodes(),
        # lines=graph.edges(),
        graph=graph
    )
    
    mygraph, constraint_junctions = topology.find_same_length_constraints(graph)
    log.image(
        width=white_balanced_image.shape[1],
        height=white_balanced_image.shape[0],
        points=constraint_junctions,
        lines=mygraph.edges(),
        graph=mygraph
    )
    
    graph = topology.simplify_paths(graph)
    log.image(
        width=white_balanced_image.shape[1],
        height=white_balanced_image.shape[0],
        points=graph.nodes(),
        lines=graph.edges()
    )
    
    graph = topology.hv_lines(graph)
    log.image(
        background=white_balanced_image,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = satisfaction.align(graph)
    log.image(
        background=white_balanced_image,
        points=graph.nodes(),
        lines=graph.edges()
    )
    
    satisfaction.apply_same_length_constraint(graph)
    
    
    
    

def sample():
    return intake.image_file("input/photo004.png")
    # return intake.image_file("input/photo003_colors.png")
