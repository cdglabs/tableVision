import cv2
import numpy as np

# Read in image
img = cv2.imread('sample.jpg')

# Convert to greyscale
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use adaptive thresholding to pick out the ink
binarized = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10)

# Show it
cv2.imshow('image', binarized)
cv2.waitKey(0)
cv2.destroyAllWindows()
