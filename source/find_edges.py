import numpy as np
import cv2
from skimage import morphology

# img is a raw color image. find_edges returns a binary image where white is edge.
def find_edges(img):
  img = cv2.medianBlur(img, 15)
  kernel = np.ones((5,5), np.uint8)
  erosion = cv2.erode(img, kernel, iterations=1)
  dilation = cv2.dilate(img, kernel, iterations=1)
  difference = dilation - erosion
  grey = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
  # cv2.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C)
  binarized = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 0)
  return binarized
