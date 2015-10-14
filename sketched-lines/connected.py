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

# Now we need to get the topology. That is, know which corner points are
# connected to which other points by lines.

# Take out little circles where the corners are to just leave the "bridges"
# between corners
bridges = binarized.copy()
for corner in corners:
  x, y = corner.ravel()
  cv2.circle(bridges, (x,y), 4, (0,0,0), -1)

cv2.imshow('bridges', bridges)

# Find contours of bridges
bridgeContours, junk = cv2.findContours(bridges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

def isConnected(point, contour):
  distance = cv2.pointPolygonTest(contour, point, True)
  return distance > -7 # Found empirically. Why this number?

lines = []
cornersLength = len(corners)
for aIndex in range(cornersLength):
  a = corners[aIndex]
  ax, ay = a.ravel()

  for bIndex in range(aIndex+1, cornersLength):
    b = corners[bIndex]
    bx, by = b.ravel()

    connectedBridges = filter(lambda contour: isConnected((ax,ay), contour) and isConnected((bx,by), contour), bridgeContours)

    if len(connectedBridges) > 0:
      lines.append((aIndex,bIndex))




# Draw lines
for line in lines:
  aIndex, bIndex = line
  a = corners[aIndex]
  ax, ay = a.ravel()
  b = corners[bIndex]
  bx, by = b.ravel()

  cv2.line(img, (ax,ay), (bx,by), (255,0,0), 2)

# Draw corners
for corner in corners:
  x, y = corner.ravel()
  cv2.circle(img, (x,y), 4, (0,255,0), -1)





# Show it
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
