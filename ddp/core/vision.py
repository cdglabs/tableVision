import numpy as np
import cv2
import random
from skimage import morphology
from Settings import Settings
import math

# img is a raw color image. find_edges returns a binary image where white
# is edge.
def find_edges(img):
    img = cv2.medianBlur(img, 15)
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(img, kernel, iterations=1)
    dilation = cv2.dilate(img, kernel, iterations=1)
    difference = dilation - erosion
    grey = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    # cv2.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C)
    binarized = cv2.adaptiveThreshold(
        grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 0)
    return binarized


# img should be a binary image showing edges. find_paper returns a contour with
# 4 points that is the outline of the paper.
def find_paper(img):
    (contours, _) = cv2.findContours(
        img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    boundingBoxes = map(
        lambda contour: (contour, cv2.boundingRect(contour)), contours)
    sortedC = sorted(
        boundingBoxes, key=lambda (contour, (x, y, w, h)): w*h, reverse=True)

    # should be the first...
    for (contour, bb) in sortedC:
        # approximate the contour
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our paper
        if len(approx) == 4:
            return approx


# img is the raw color image. paper is the contour with four-points that
# outlines the paper in img.
# TODO still unstable. may not find borders. may not find correct orientation (upside down)
def extract_paper(img, paper, is_upside_down = True):
    assert len(paper) == 4
    # Ensure that paper coordinates are specified clockwise.
    clockwise = cv2.contourArea(paper, True) > 0
    if not clockwise:
        paper = np.flipud(paper)
    
    # Ensure that the paper is in "landscape" as opposed to portrait view.
    length_edge1 = np.linalg.norm(paper[0] - paper[1])
    length_edge2 = np.linalg.norm(paper[0] - paper[3])
    if length_edge2 > length_edge1:
        # Portrait, so rotate once.
        paper = np.roll(paper, 1, axis=0)
    
    paper = paper.astype(np.float32)
    
    w = int(Settings.PAPER_LONG_SIDE_MM * Settings.PIXELS_PER_MM)
    h = int(Settings.PAPER_SHORT_SIDE_MM * Settings.PIXELS_PER_MM)
    model_paper_normal = [ (0,0), (w,0), (w,h), (0,h) ]
    model_paper_upside_down = [ (w,h), (0,h), (0,0), (w,0) ]
    model_paper = model_paper_upside_down if is_upside_down else model_paper_normal
    
    source = np.array(model_paper, np.float32)
    transformMatrix = cv2.getPerspectiveTransform(paper, source)
    transformed = cv2.warpPerspective(img, transformMatrix, (w, h))
    return transformed


def delete_margins_from_binary_image(binarized, margin_percent = 0.01):
    (height, width) = binarized.shape
    margin = int(margin_percent * min(width, height)) 
    cv2.rectangle(binarized, (0, 0), (width, margin), 0, -1)
    cv2.rectangle(binarized, (0, 0), (margin, height), 0, -1)
    cv2.rectangle(binarized, (width-margin, 0), (width, height), 0, -1)
    cv2.rectangle(binarized, (0, height-margin), (width, height), 0, -1)
    return binarized


# img is a color image of paper with ink. binarize_ink returns a binary image
# where ink is white, paper is black.
def binarize_ink(img):
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blockSize = 45
    threshold = 50  # Constant subtracted from the mean or weighted mean
    # http://docs.opencv.org/2.4/modules/imgproc/doc/miscellaneous_transformations.html
    binarized = cv2.adaptiveThreshold(
        grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        blockSize, threshold
    )

    # Delete margins. That is, make sure the edges of the paper don't get
    # picked up as ink.
    binarized = delete_margins_from_binary_image(binarized)
    return binarized


def binarize_ink_IMPROVED(grey):
    stroke_width_px_int = int( math.ceil( Settings.STROKE_WIDTH_MM * Settings.PIXELS_PER_MM ) )
    # Size of a pixel neighborhood that is used to calculate a threshold value
    blockSize = stroke_width_px_int * 25
    noise_reduction = 25
    def uneven(x): return x + x % 2 + 1
    # http://docs.opencv.org/2.4/modules/imgproc/doc/miscellaneous_transformations.html
    binarized = cv2.adaptiveThreshold(
        grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        uneven(blockSize), noise_reduction
    )
    filtered = remove_noise_from_binary_image(binarized)
    filtered = delete_margins_from_binary_image(filtered)
    return filtered


def white_balance(inimg, randomPoolSize = 100, selectionPoolSize = 20):
    img = inimg.copy()
    height, width, colors = img.shape  # y, x, color
    randomPixels = map(
        lambda id: img[
            random.randint(0, height-1),
            random.randint(0, width-1)
        ],
        range(0, randomPoolSize)
    )
    randomPixels = map(
        lambda gbr: (int(gbr[2]), int(gbr[0]), int(gbr[1])),
        randomPixels
    )
    filtered = filter(
        lambda (r, g, b): r < 255 and g < 255 and b < 255,
        randomPixels
    )
    sortedArr = sorted(filtered, key=lambda (r, g, b): r+g+b)
    brigthest = sortedArr[max(0, len(sortedArr)-selectionPoolSize):]
    (r, g, b) = reduce(
        lambda (r1, g1, b1), (r2, g2, b2): (r1+r2, g1+g2, b1+b2),
        brigthest, (0, 0, 0)
    )
    (r, g, b) = (r/len(brigthest), g/len(brigthest), b/len(brigthest))
    average = (r+g+b)/3
    (dr, dg, db) = (r-average, g-average, b-average)
    #~ print (dr, dg, db)
    # avert overflow of uint8 [0,255]
    img[:, :, :] *= (255-max(dr, dg, db))/255.0
    img[:, :, :] += max(dr, dg, db)
    img[:, :, 0] -= dg
    img[:, :, 1] -= db
    img[:, :, 2] -= dr
    return img


# img is a binary image where ink is white, paper is black. This
# "skeletonizes" the image, so that all lines are "thinned" to a single pixel.
def skeletonize(img):
    skeleton = morphology.skeletonize(img > 0)
    skeleton = skeleton.astype(np.uint8)
    skeleton = skeleton * 255
    return skeleton


def remove_noise_from_binary_image(binary_image):
    (contours, _) = cv2.findContours(binary_image.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    threshold_size = 40
    small_blobs = []
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) < threshold_size:
            small_blobs.append(contours[i])

    # flood fill small blobs with black
    cv2.drawContours(binary_image, small_blobs, -1, 0, thickness=-1)
    return binary_image


def convert_hsv_image_to_greyscale_emphasising_saturation(hsv):
    # problem: normal cv2.COLOR_BGR2GRAY converts to a very light grey for, say, yellow strokes
    # grey = cv2.cvtColor(white_balanced_image, cv2.COLOR_BGR2GRAY)
    # convert to grey emphasising saturation!
    hsv_factors = [0, -2, 1]
    mat = np.array(hsv_factors).reshape((1,3))
    myGrey = cv2.transform(hsv, mat)
    return myGrey
