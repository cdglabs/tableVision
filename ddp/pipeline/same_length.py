import cv2
import infrastructure.log as log
import infrastructure.intake as intake
from core import vision
import numpy as np
import core.vision as vision
import core.topology as topology
import math

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph
from pipeline.hv_lines import run as hv_lines


def find_ranges(colorDict):
    colorsList = sorted(colorDict.items(), key=lambda (key, value): value)
    assert len(colorsList) > 1
    result = {}
    for i, (key, value) in enumerate(colorsList):
        nextLower = colorsList[i-1][1]  # works fine if i == 0
        nextHigher = colorsList[i+1 if i<len(colorsList)-1 else 0][1]
        
        # need to take care of wrapping numbers. it is a color WHEEL afterall
        if nextLower > value:
            nextLower -= 180
        if nextHigher < value:
            nextHigher += 180
            
        def mean(a,b):
            return a+abs(b-a)/2 if a<b else b+abs(a-b)/2
        
        result[key] = [(mean(value, nextLower), mean(nextHigher, value))]
        if result[key][0][0] < 0:
            result[key] = [(0, mean(nextHigher, value))]
            result[key].append((mean(value, nextLower) + 180, 179))
        if result[key][0][1] > 179:
            result[key] = [(mean(value, nextLower), 179)]
            result[key].append((0, mean(nextHigher, value) - 180))
    return result
        







def getColourComponents(white_balanced_image):
    hsv_image = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)
    # color centers:
    # 0=180 red
    baseColorsCenter = {'red': 0, 'yellow': 30, 'green': 60, 'aqua': 90, 'blue': 120, 'violett': 150}
    # colorRanges = findRanges(baseColorsCenter)
    # empirically obtained, best colors to use: Sharpie
    colorRanges = {
        'red': [(0, 15, 70, 100),
                (155, 180, 70, 100)],
        'yellow': [(18, 30, 60, 100)],
        'green': [(35, 82, 70, 30)],
        'blue aqua': [(90, 110, 50, 100)],
        'violett': [(120, 150, 100, 60)],
    }
    # colorRanges = {
    #     'red': [(0, 15), (175, 179)],
    #     'yellow': [(15, 29)],
    #     'green': [(30, 90)],
    #     'blue': [(90, 120)],
    #     'violett': [(120, 140)],
    #     'purple': [(140, 172)]
    # }
    
    colorImages = {}
    for key, list in colorRanges.iteritems():
        assert len(list) == 1 or len(list) == 2
        # Python: cv2.inRange(src, lowerb, upperb[, dst])  dst
        # For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
        # note: Value 255 is not white, as in HSL, but a fully bright color
        colorImages[key] = cv2.inRange(hsv_image, (list[0][0], list[0][2], list[0][3]), (list[0][1], 255, 255))
        if (len(list) == 2):
            secondCompound = cv2.inRange(hsv_image, (list[1][0], list[0][2], list[0][3]), (list[1][1], 255, 255))
            colorImages[key] = cv2.addWeighted(colorImages[key], 1.0, secondCompound, 1.0, 0.0)
        # log.image(colorImages[key])
        # kernel = np.ones((1, 1), np.uint8)
        # erosion = cv2.erode(colorImages[key], kernel, iterations=1)
        # dilation = cv2.dilate(erosion, kernel, iterations=1)
        # log.image(dilation)
    
    return colorImages
     

def run(img):
    # log.image(img)
    extracted = extract_paper(img, logOn=False)
    white_balanced_image = vision.white_balance(extracted)
    # log.image(white_balanced_image)
    hsv = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)
    
    stroke_width_mm = 0.2  # Sharpie ultra fine
    # TODO globalise
    pixels_per_mm = 10
    stroke_width_px_int = int( math.ceil( stroke_width_mm * pixels_per_mm ) )
    # print mean_pixels_per_mm
    
    # problem: normal cv2.COLOR_BGR2GRAY converts to a very light grey for, say, yellow strokes
    # convert to grey emphasising saturation!
    hsv_factors = [0, -2, 1]
    mat = np.array(hsv_factors).reshape((1,3))
    myGrey = cv2.transform(hsv, mat)
    # log.image(myGrey)
    
    # grey = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2GRAY)
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
    
    # colorImages = getColourComponents(white_balanced_image)
    

    # for cImg in colorImages:
    #     skeleton = vision.skeletonize(cImg)
        # log.image(background=skeleton)
    
        # graph = topology.produce_graph(skeleton)
        # log.image(
        #     background=img,
        #     pixels=graph.nodes()
        # )
        # log.gpickle(graph)
    
        # graph = topology.simplify_junctures(graph)
        # log.image(
        #     background=img,
        #     points=(node for node in graph.nodes() if graph.degree(node) != 2)
        # )
    
        # skeleton = removeSmallContours(skeleton)
        # log.image(background=skeleton)
    
        # graph = topology.produce_graph(skeleton)
        # log.image(
        #     background=img,
        #     pixels=graph.nodes()
        # )
        # log.gpickle(graph)
        
        
    
    


def sample():
    return intake.image_file("input/photo004.png")
    # return intake.image_file("input/photo003_colors.png")
