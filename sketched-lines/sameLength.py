import cv2
import numpy as np

# Read in image
img = cv2.imread('sample3_cut,whiteBalanced.png')


hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

#~ Threshold the HSV image, keep only the red pixels
#Python: cv2.inRange(src, lowerb, upperb[, dst])  dst
# For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
lower_red_hue_range = cv2.inRange(hsv_image, (0, 190, 50), (20, 255, 255))
upper_red_hue_range = cv2.inRange(hsv_image, (160, 190, 50), (179, 255, 255))
red_hue_image = cv2.addWeighted(lower_red_hue_range, 1.0, upper_red_hue_range, 1.0, 0.0)

# TODO: connect red component paths / find crossings

# Show it
cv2.imshow('image', red_hue_image)
#cv2.imshow('image2', lower_red_hue_range)
cv2.waitKey(0)
cv2.destroyAllWindows()
