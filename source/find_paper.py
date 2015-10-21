import numpy as np
import cv2
from skimage import morphology

# img should be a binary image showing edges. findPaper returns a contour with
# 4 points that is the outline of the paper.
def find_paper(img):
	(contours, _) = cv2.findContours(img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	boundingBoxes = map(lambda contour: (contour, cv2.boundingRect(contour)), contours)
	sortedC = sorted(boundingBoxes, key=lambda (contour, (x,y,w,h)): w*h, reverse=True)
	
	# should be the first...
	for (contour, bb) in sortedC:
		# approximate the contour
		perimeter = cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
		# if our approximated contour has four points, then we
		# can assume that we have found our paper
		if len(approx) == 4:
			return approx
