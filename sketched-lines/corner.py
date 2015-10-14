import cv2
import numpy as np

# Read in image
img = cv2.imread('sample.jpg')

# Convert to greyscale
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use adaptive thresholding to pick out the ink
binarized = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10)

# Find corners. Parameters:
# 1. How many corners to find.
# 2. Quality of corners (0 - 1)
# 3. Minimum distance between corners
corners = cv2.goodFeaturesToTrack(binarized, 200, 0.5, 10)

# Draw corners on original image
corners = np.int0(corners)
for i in corners:
    x,y = i.ravel()
    cv2.circle(img,(x,y),3,(0,0,255),-1)

# Show it
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
