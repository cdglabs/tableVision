import random, math
import numpy as np
import cv2

import log


def find_paper(img):
    # Convert to grey, emphasizing saturation.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_factors = [0, -2, 1]
    mat = np.array(hsv_factors).reshape((1,3))
    img = cv2.transform(hsv, mat)
    log.image_grey(img)
    
    # Binarize.
    binarized = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 3 )
    log.image_grey(binarized)
    
    # Find paper contour.
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
            print approx
            log.image_grey(img, log.contours([approx]))
            return approx
    
    
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
    log.image(img)
    return img
    
    
    
    
def main():
    img = cv2.imread("../input/curves.jpg")
    log.image(img)
    img = white_balance(img)
    paper_contour = find_paper(img)
    # img = white_balance(img)

if __name__ == "__main__":
    main()
