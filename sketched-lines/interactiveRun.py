import cv2
import numpy as np
import sys

assert len(sys.argv) > 1, "first command line argument must be module name to run"
print "running: "+sys.argv[1]
moduleToRun = __import__(sys.argv[1])
methodNameToRun = "withImage"
assert hasattr(moduleToRun, methodNameToRun), "module has to have "+methodNameToRun+" method"

cap = cv2.VideoCapture(1)
# resolution
cap.set(3, 1920)
cap.set(4, 1080)

moduleToRun = reload(moduleToRun)

while(True):
	try:
		moduleToRun = reload(moduleToRun)
		ret, frame = cap.read()
		result = getattr(moduleToRun, methodNameToRun)(frame)
		if isinstance(result, list):
			for i in range(len(result)):
				windowName = 'frame'+str(i)
				cv2.imshow(windowName, result[i])
				#cv2.moveWindow(windowName, 100, 100)
		else:
			cv2.imshow('frame', result)
	except:
		#~ pass
		raise
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
