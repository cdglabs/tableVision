import cv2
import numpy as np

tileNo = 0
mouse = (0, 0)

def render4(a, frame):
	global tileNo
	width = 1280
	height = 720
	resizedFrame = cv2.resize(frame, (width/2, height/2))
	#print resizedFrame.shape
	#print len(frame.shape)
	y = slice(0, height/2) if tileNo<2 else slice(height/2, height)
	x = slice(0, width/2) if tileNo % 2 == 0 else slice(width/2, width)
	if len(frame.shape) == 3:
		a[y, x, (2,1,0)] = resizedFrame
	else:
		a[y, x, 0] = resizedFrame
		a[y, x, 1] = resizedFrame
		a[y, x, 2] = resizedFrame
	tileNo = (tileNo+1) % 4
	#a[:,:,(2,1,0)] = result #value set
	#a = frame #pointer set

def video_out(a):
	global tileNo
	tileNo = 0
	a[:] = 240 # y,x,color
	a[10:30,10:30,] = 0 # black square
	frame = gen.next()
	#print frame.shape
	kernel = np.ones((7,7), np.uint8)
	
	erosion = cv2.erode(frame, kernel, iterations = 1)
	render4(a, erosion)
	dilation = cv2.dilate(frame, kernel, iterations = 1)
	render4(a, dilation)
	#result = cv2.subtract(erosion, dilation)
	#result = (dilation.astype(int) - erosion).clip(0, 255).astype(np.uint8)
	result = dilation - erosion
	render4(a, result)
	
	#grey = (result[:,:,0]+result[:,:,1]+result[:,:,2])/3
	grey = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
	render4(a, grey)
	
	ret2,th2 = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	render4(a, th2)
	
	#cv2.findContours(th2, mode, method[, contours[, hierarchy[, offset]]]) → contours, hierarchy
	contours, hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	maxContour = max(contours, key=lambda contour: cv2.contourArea(contour))
	cv2.drawContours(frame, [maxContour], -1, (0,255,0), 3)
	render4(a, frame)
	
	#approximate contour with accuracy proportional to the contour perimeter
	epsilon = cv2.arcLength(maxContour, True)*0.02
	ap = cv2.approxPolyDP(maxContour, epsilon, True)
	#figure out the orientation of the contour to match horizontal orientation
	dist01 = np.linalg.norm(ap[0] - ap[1])
	#dist02 = np.linalg.norm(ap[0] - ap[2]) #diagonal
	dist03 = np.linalg.norm(ap[0] - ap[3])
	horizontal = dist01 > dist03
	approxCurve = np.array([ap[0] if horizontal else ap[1], ap[1] if horizontal else ap[2], ap[2] if horizontal else ap[3], ap[3] if horizontal else ap[0]])
	
	cv2.drawContours(frame, [approxCurve], -1, (0,0,255), 2)
	render4(a, frame)
	
	# us letter: 8.5 by 11
	source = np.array([[0,850], [1100,850], [1100,0], [0,0]], np.float32)
	target = np.array([approxCurve[0], approxCurve[1], approxCurve[2], approxCurve[3]], np.float32)
	transformMatrix = cv2.getPerspectiveTransform(target, source)
	# cv2.warpPerspective(src, M, dsize[, dst[, flags[, borderMode[, borderValue]]]]) → dst¶
	transformed = cv2.warpPerspective(frame, transformMatrix, (1280, 720))
	render4(a, transformed)
	
	# print color of pixel under mouse
	if mouse[0] == "mouse-button-press":
		print a[mouse[2], mouse[1]]
	
	
def mouse_in(type, x, y, button):
	global mouse
	mouse = (type, x, y, button)
	#print "bla"
	

	