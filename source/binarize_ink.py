import numpy as np
import cv2
from skimage import morphology

# img is a color image of paper with ink. binarize_ink returns a binary image
# where ink is white, paper is black.
def binarize_ink(img):
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
