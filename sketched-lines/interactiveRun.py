import cv2
import numpy as np
import sys

useLiveVideo=False
runInteractive=True
moduleToRun=None
methodNameToRun = "withImage"
frame=None
capture=None

def setUpModuleToBeRun():
	assert len(sys.argv) > 1, "first command line argument must be module name to run"
	print "running: "+sys.argv[1]
	moduleToRun = __import__(sys.argv[1])
	assert hasattr(moduleToRun, methodNameToRun), "module has to have "+methodNameToRun+" method"
	return moduleToRun

def runOnce(moduleToRun):
	global frame, methodNameToRun, capture
	try:
		moduleToRun = reload(moduleToRun)
		if useLiveVideo:
			ret, frame = capture.read()
		result = getattr(moduleToRun, methodNameToRun)(frame)
		if isinstance(result, list):
			for i in range(len(result)):
				windowName = 'frame'+str(i)
				cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
				#cv2.resizeWindow(windowName, 900, 600)
				#cv2.moveWindow(windowName, 100, 100)
				cv2.imshow(windowName, result[i])
		else:
			cv2.imshow('frame', result)
	except:
		#~ pass
		raise
	
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
		frame = cv2.imread("photo001.jpg")
	
	if runInteractive:
		moduleToRun = reload(moduleToRun)
		while(True):
			if runOnce(moduleToRun) == True:
				break
	else:
		runOnce(moduleToRun)
	
	if useLiveVideo:
		capture.release()
	cv2.destroyAllWindows()

main()
