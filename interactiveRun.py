import cv2
import numpy as np
import sys
import math

useLiveVideo=False
runInteractive=True
moduleToRun=None
methodNameToRun = "withImage"
frame=None
capture=None
firstRun=True

def setUpModuleToBeRun():
	assert len(sys.argv) > 1, "first command line argument must be module name to run"
	print "running: "+sys.argv[1]
	moduleToRun = __import__(sys.argv[1])
	assert hasattr(moduleToRun, methodNameToRun), "module has to have "+methodNameToRun+" method"
	return moduleToRun

def runOnce(moduleToRun):
	global frame, methodNameToRun, capture, firstRun
	try:
		moduleToRun = reload(moduleToRun)
		if useLiveVideo:
			ret, frame = capture.read()
		result = getattr(moduleToRun, methodNameToRun)(frame)
		
		if not isinstance(result, list):
			result = [result]
		size = len(result)
		matrixDim = int(math.ceil(math.sqrt(size)))
		totalWidth=1920
		totalHeight=1080
		winWidth=totalWidth/matrixDim
		winHeight=totalHeight/matrixDim
		for i in range(size):
			x = i % matrixDim
			y = i / matrixDim
			windowName = 'frame '+str(i)
			cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
			if firstRun: # let the user move windows around in a custom fashion
				cv2.resizeWindow(windowName, winWidth, winHeight)
				cv2.moveWindow(windowName, x*winWidth, y*winHeight)
			cv2.imshow(windowName, result[i])
	except:
		#~ pass
		raise
	
	if firstRun:
		firstRun=False
	if cv2.waitKey(1) & 0xFF == ord('q'):
		return True #break

def main():
	global frame, capture
	moduleToRun = setUpModuleToBeRun()
	
	if useLiveVideo:
		capture = cv2.VideoCapture(0)
		# resolution
		capture.set(3, 1920)
		capture.set(4, 1080)
	else:
		frame = cv2.imread("input/photo002.jpg")
	
	if runInteractive:
		moduleToRun = reload(moduleToRun)
		while(True):
			if runOnce(moduleToRun) == True:
				break
	else:
		runOnce(moduleToRun)
	
	if not runInteractive:
		cv2.waitKey(0)
	if useLiveVideo:
		capture.release()
	cv2.destroyAllWindows()

main()
