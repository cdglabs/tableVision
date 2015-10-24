import cv2
import infrastructure.log as log
import infrastructure.intake as intake
from core import vision


def run(img):
    log.image(img)
    edges = vision.find_edges(img)
    paper = vision.find_paper(edges)
    extracted = vision.extract_paper(img, paper)
    log.image(extracted)

    white_balanced_image = vision.white_balance(extracted)
    log.image(white_balanced_image)
    hsv_image = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2HSV)

    # TODO: connect red component paths / find crossings
    #~ Threshold the HSV image, keep only the red pixels
    #Python: cv2.inRange(src, lowerb, upperb[, dst])  dst
    # For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
    lower_red_hue_range = cv2.inRange(hsv_image, (0, 190, 50), (60, 255, 255))
    upper_red_hue_range = cv2.inRange(hsv_image, (160, 190, 50), (179, 255, 255))
    red_hue_image = cv2.addWeighted(lower_red_hue_range, 1.0, upper_red_hue_range, 1.0, 0.0)
    log.image(red_hue_image)


def sample():
    return intake.image_file("input/photo002.jpg")
