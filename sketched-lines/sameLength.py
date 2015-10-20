import cv2
import numpy as np
import random

def whiteBalance(img):
	height, width, colors = img.shape #y, x, color
	randomPixels = map(lambda id: (id, img[random.randint(0, height-1), random.randint(0, width-1)]), range(0, 20))
	randomPixels = map(lambda (id, gbr): (id, (int(gbr[2]), int(gbr[0]), int(gbr[1]))), randomPixels)
	sum = map(lambda (id, (r, g, b)): (id, r+g+b), randomPixels)
	(id, maxGray) = max(sum, key=lambda (id, grey): grey)
	(r, g, b) = randomPixels[id][1]
	print (r, g, b)
	average = (r+g+b)/3
	print average
	(dr, dg, db) = (r-average, g-average, b-average)
	print (dr, dg, db)
	print type(img[0,0])
	print type(img[0,0,0])
	
	# TODO shift rgb by dr, dg, db
	#~ np.add(img, 20)
	
	#~ for i in range(0, height):
		#~ for j in range(0, width):
			#~ b,g,r = cv2.get2D(img, i, j)
			#~ cv2.set2D(img, i, j, [g - dg, b - db, r - dr])
	
	#~ for y in range(0, height-1):
		#~ for x in range(0, width-1):
			#~ img[y, x] = np.array([img[y, x][0] - dg, img[y, x][1] - db, img[y, x][2] - dr])
	return img
	

def withImage(img):
	whiteBalancedImage = whiteBalance(img)
	hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# balanceWhite
	# TODO: connect red component paths / find crossings

	#~ Threshold the HSV image, keep only the red pixels
	#Python: cv2.inRange(src, lowerb, upperb[, dst])  dst
	# For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
	lower_red_hue_range = cv2.inRange(hsv_image, (0, 190, 50), (20, 255, 255))
	upper_red_hue_range = cv2.inRange(hsv_image, (160, 190, 50), (179, 255, 255))
	red_hue_image = cv2.addWeighted(lower_red_hue_range, 1.0, upper_red_hue_range, 1.0, 0.0)
	
	return [img, whiteBalancedImage]
