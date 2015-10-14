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


# Determine horizontal and vertical constraints by partitioning lines based on
# whether they are more horizontal or vertical.
horizontalConstraints = []
verticalConstraints = []
for line in lines:
  aIndex, bIndex = line
  a = corners[aIndex]
  ax, ay = a.ravel()
  b = corners[bIndex]
  bx, by = b.ravel()
  dx = abs(ax - bx)
  dy = abs(ay - by)
  if dx > dy:
    horizontalConstraints.append((aIndex, bIndex))
  else:
    verticalConstraints.append((aIndex, bIndex))


def connectedConstraints(constraint, constraints):
  a, b = constraint
  return filter(lambda c: c[0] == a or c[0] == b or c[1] == a or c[1] == b, constraints)

def allConnectedConstraints(constraint, constraints):
  result = set([])
  def addToResult(c):
    if c in result:
      return
    result.add(c)
    for connectedConstraint in connectedConstraints(c, constraints):
      addToResult(connectedConstraint)
  addToResult(constraint)
  return result

for constraint in horizontalConstraints:
  inLineConstraints = allConnectedConstraints(constraint, horizontalConstraints)
  points = set([])
  for c in inLineConstraints:
    points.add(c[0])
    points.add(c[1])
  averageY = 0
  for point in points:
    (x, y) = corners[point].ravel()
    averageY = averageY + y
  averageY = averageY / len(points)
  for point in points:
    corners[point][0][1] = averageY

for constraint in verticalConstraints:
  inLineConstraints = allConnectedConstraints(constraint, verticalConstraints)
  points = set([])
  for c in inLineConstraints:
    points.add(c[0])
    points.add(c[1])
  averageX = 0
  for point in points:
    (x, y) = corners[point].ravel()
    averageX = averageX + x
  averageX = averageX / len(points)
  for point in points:
    corners[point][0][0] = averageX









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
