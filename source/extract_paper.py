import numpy as np
import cv2
from skimage import morphology

# img is the raw color image. paper is the contour with four-points that
# outlines the paper in img. extract_paper returns a color image that is
# 1100x850 (US Letter paper) of the perspective-corrected paper.
def extract_paper(img, paper):
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
