import numpy as np
import cv2
import random
from skimage import morphology


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
# outlines the paper in img. extract_paper returns a color image that is
# 1100x850 (US Letter paper) of the perspective-corrected paper.
def extract_paper(img, paper):
    # Figure out the orientation.
    dist01 = np.linalg.norm(paper[0] - paper[1])
    dist03 = np.linalg.norm(paper[0] - paper[3])
    horizontal = dist01 > dist03
    paper = np.array([
        paper[0] if horizontal else paper[1],
        paper[1] if horizontal else paper[2],
        paper[2] if horizontal else paper[3],
        paper[3] if horizontal else paper[0]
    ], np.float32)

    # us letter: 8.5 by 11
    source = np.array([[0, 850], [1100, 850], [1100, 0], [0, 0]], np.float32)
    transformMatrix = cv2.getPerspectiveTransform(paper, source)
    transformed = cv2.warpPerspective(img, transformMatrix, (1100, 850))
    return transformed


# img is a color image of paper with ink. binarize_ink returns a binary image
# where ink is white, paper is black.
def binarize_ink(img):
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blockSize = 45
    threshold = 6
    binarized = cv2.adaptiveThreshold(
        grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        blockSize, threshold
    )

    # Delete margins. That is, make sure the edges of the paper don't get
    # picked up as ink.
    margin = 20
    (height, width) = binarized.shape
    cv2.rectangle(binarized, (0, 0), (width, margin), 0, -1)
    cv2.rectangle(binarized, (0, 0), (margin, height), 0, -1)
    cv2.rectangle(binarized, (width-margin, 0), (width, height), 0, -1)
    cv2.rectangle(binarized, (0, height-margin), (width, height), 0, -1)

    return binarized


def white_balance(img):
    randomPoolSize = 100
    selectionPoolSize = 20
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
