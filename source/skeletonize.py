import numpy as np
import cv2
from skimage import morphology

# img is a binary image where ink is white, paper is black. This
# "skeletonizes" the image, so that all lines are "thinned" to a single pixel.
def skeletonize(img):
  skeleton = morphology.skeletonize(img > 0)
  skeleton = skeleton.astype(np.uint8)
  skeleton = skeleton * 255
  return skeleton
