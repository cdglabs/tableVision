import cv2
import infrastructure.log as log
import infrastructure.intake as intake
from core import vision
import numpy as np
import core.vision as vision
import core.topology as topology


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
        

def remove_small_contours(binary_image):
    (contours, _) = cv2.findContours(binary_image.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    threshold = 0
    small_blobs = []
    for idx, contour in enumerate(contours):
        if cv2.contourArea(contour) < threshold:
            cv2.drawContours(binary_image, contours, idx, 0)
            # print idx
    
    # cv2.drawContours(image, contours, contourIdx, color[, thickness[, lineType[, hierarchy[, maxLevel[, offset]]]]])
    return binary_image


def run(img):
    # img = cv2.flip(img,-1)
    log.image(img)
    
    # edges = vision.find_edges(img)
    # paper = vision.find_paper(edges)
    # extracted = vision.extract_paper(img, paper)
    # log.image(extracted)

    white_balanced_image = vision.white_balance(img)
    # log.image(white_balanced_image)
    hsv_image = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)

    # TODO: connect red component paths / find crossings
    #~ Threshold the HSV image, keep only the red pixels
    #Python: cv2.inRange(src, lowerb, upperb[, dst])  dst
    # For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
    # note: Value 255 is not white, as in HSL, but a fully bright color
    satStart = 70
    valStart = 30
    
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
        colorImages[key] = cv2.inRange(hsv_image, (list[0][0], list[0][2], list[0][3]), (list[0][1], 255, 255))
        if (len(list) == 2):
            secondCompound = cv2.inRange(hsv_image, (list[1][0], list[0][2], list[0][3]), (list[1][1], 255, 255))
            colorImages[key] = cv2.addWeighted(colorImages[key], 1.0, secondCompound, 1.0, 0.0)
        # log.image(colorImages[key])
        # kernel = np.ones((1, 1), np.uint8)
        # erosion = cv2.erode(colorImages[key], kernel, iterations=1)
        # dilation = cv2.dilate(erosion, kernel, iterations=1)
        # log.image(dilation)
        
        skeleton = vision.skeletonize(colorImages[key])
        # log.image(background=skeleton)
        
        graph = topology.produce_graph(skeleton)
        # log.image(
        #     background=img,
        #     pixels=graph.nodes()
        # )
        # log.gpickle(graph)
        
        graph = topology.simplify_junctures(graph)
        log.image(
            background=img,
            points=(node for node in graph.nodes() if graph.degree(node) != 2)
        )
        
        # skeleton = removeSmallContours(skeleton)
        # log.image(background=skeleton)
    
        # graph = topology.produce_graph(skeleton)
        # log.image(
        #     background=img,
        #     pixels=graph.nodes()
        # )
        # log.gpickle(graph)
        
        
    
    


def sample():
    return intake.image_file("input/photo004_cut.png")
    # return intake.image_file("input/photo003_colors.png")
