import cv2
import random

def white_balance(img):
	randomPoolSize = 100
	selectionPoolSize = 20
	height, width, colors = img.shape #y, x, color
	randomPixels = map(lambda id: img[random.randint(0, height-1), random.randint(0, width-1)], range(0, randomPoolSize))
	randomPixels = map(lambda gbr: (int(gbr[2]), int(gbr[0]), int(gbr[1])), randomPixels)
	filtered = filter(lambda (r, g, b): r<255 and g<255 and b<255, randomPixels)
	sortedArr = sorted(filtered, key=lambda (r, g, b): r+g+b)
	brigthest = sortedArr[max(0, len(sortedArr)-selectionPoolSize):]
	(r, g, b) = reduce(lambda (r1, g1, b1), (r2, g2, b2): (r1+r2, g1+g2, b1+b2), brigthest, (0,0,0))
	(r, g, b) = (r/len(brigthest), g/len(brigthest), b/len(brigthest))
	average = (r+g+b)/3
	(dr, dg, db) = (r-average, g-average, b-average)
	#~ print (dr, dg, db)
	# avert overflow of uint8 [0,255]
	img[:,:,:] *= (255-max(dr, dg, db))/255.0
	img[:,:,:] += max(dr, dg, db)
	img[:,:,0] -= dg
	img[:,:,1] -= db
	img[:,:,2] -= dr
	return img
