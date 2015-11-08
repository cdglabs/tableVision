import infrastructure.intake as intake
import infrastructure.log as log

import core.vision as vision
import numpy as np
import cv2


def run(img, logOn=True):
    white_balanced_image = vision.white_balance(img)
    hsv = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)
    if logOn: log.hsvOrGreyImage(hsv)
    
    edges = vision.find_edges(hsv)
    if logOn: log.hsvOrGreyImage(edges)
    
    paper_contour = vision.find_paper(edges)
    if logOn: log.hsvOrGreyImage(hsv, contours=[paper_contour])
    
    extracted = vision.extract_paper(hsv, paper_contour)
    if logOn: log.hsvOrGreyImage(extracted)
    
    return extracted


def sample():
    return intake.image_file("input/grid_drawing.jpg")
