import numpy as np
import cv2
from skimage import morphology


# img is a raw color image. findEdges returns a binary image where white is edge.
def findEdges(img):
  kernel = np.ones((5,5), np.uint8)
  erosion = cv2.erode(img, kernel, iterations=1)
  dilation = cv2.dilate(img, kernel, iterations=1)
  difference = dilation - erosion
  grey = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
  (_, binarized) = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  return binarized

  # grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # blurred = cv2.GaussianBlur(grey, (5, 5), 0)
  # edged = cv2.Canny(blurred, 20, 120)
  # return edged


# img should be a binary image showing edges. findPaper returns a contour with
# 4 points that is the outline of the paper.
def findPaper(img):
  (contours, _) = cv2.findContours(img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
  contours = sorted(contours, key = cv2.contourArea, reverse = True)

  # loop over the contours
  for contour in contours:
    # approximate the contour
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

    # if our approximated contour has four points, then we
    # can assume that we have found our paper
    if len(approx) == 4:
      return approx


# img is the raw color image. paper is the contour with four-points that
# outlines the paper in img. extractPaper returns a color image that is
# 1100x850 (US Letter paper) of the perspective-corrected paper.
def extractPaper(img, paper):
  # Figure out the orientation.
  dist01 = np.linalg.norm(paper[0] - paper[1])
  dist03 = np.linalg.norm(paper[0] - paper[3])
  horizontal = dist01 > dist03
  paper = np.array([paper[0] if horizontal else paper[1], paper[1] if horizontal else paper[2], paper[2] if horizontal else paper[3], paper[3] if horizontal else paper[0]], np.float32)

  # us letter: 8.5 by 11
  source = np.array([[0,850], [1100,850], [1100,0], [0,0]], np.float32)
  transformMatrix = cv2.getPerspectiveTransform(paper, source)
  transformed = cv2.warpPerspective(img, transformMatrix, (1100, 850))
  return transformed


# img is a color image of paper with ink. binarizeInk returns a binary image
# where ink is white, paper is black.
def binarizeInk(img):
  grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blockSize = 45
  threshold = 6
  binarized = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize, threshold)

  # Delete margins. That is, make sure the edges of the paper don't get picked up as ink.
  margin = 20
  (height, width) = binarized.shape
  cv2.rectangle(binarized, (0,0), (width,margin), 0, -1)
  cv2.rectangle(binarized, (0,0), (margin,height), 0, -1)
  cv2.rectangle(binarized, (width-margin,0), (width,height), 0, -1)
  cv2.rectangle(binarized, (0,height-margin), (width,height), 0, -1)

  return binarized


# img is a binary image where ink is white, paper is black. This
# "skeletonizes" the image, so that all lines are "thinned" to a single pixel.
def skeletonize(img):
  skeleton = morphology.skeletonize(img > 0)
  skeleton = skeleton.astype(np.uint8)
  skeleton = skeleton * 255
  return skeleton








# Parameter specifies which webcam to use. See order in e.g. Photo Booth's
# Camera menu.
cap = cv2.VideoCapture(1)

while(True):
  # Capture frame-by-frame
  junk, frame = cap.read()

  edges = findEdges(frame)
  # cv2.imshow("out", edges)

  paper = findPaper(edges)
  # out = frame.copy()
  # cv2.drawContours(out, [paper], -1, (0,0,255), 2)
  # cv2.imshow("out", out)

  extracted = extractPaper(frame, paper)
  # cv2.imshow("out", extracted)

  ink = binarizeInk(extracted)
  # cv2.imshow("out", ink)

  skeleton = skeletonize(ink)
  cv2.imshow("out", skeleton)



  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
