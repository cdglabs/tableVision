import cv2
import numpy as np
import sys

assert len(sys.argv) > 1, "first command line argument must be module name to run"
print "running: "+sys.argv[1]
moduleToRun = __import__(sys.argv[1])
methodNameToRun = "withImage"
assert hasattr(moduleToRun, methodNameToRun), "module has to have "+methodNameToRun+" method"

cap = cv2.VideoCapture(1)

while(True):
	try:
		# watch file changes for interactive workflow
		moduleToRun = reload(moduleToRun)
		ret, frame = cap.read()
		#result = moduleToRun.withImage(frame)
		result = getattr(moduleToRun, methodNameToRun)(frame)
	except:
		pass
	
	cv2.imshow('frame', result)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
#cv2.imshow('image', red_hue_image)
#cv2.waitKey(0)
cv2.destroyAllWindows()
