import numpy as np
import cv2
import os.path

cap = cv2.VideoCapture(1)

filenameNumber = 1
getFilename = lambda: os.getcwd()+"/"+"capture"+str(filenameNumber)+".png"
while os.path.isfile(getFilename()):
	filenameNumber += 1
	
# take 3, because the first couple may be screwed
ret, frame = cap.read()
ret, frame = cap.read()
ret, frame = cap.read()

print "saving to: "+getFilename()
cv2.imwrite(getFilename(), frame)

cap.release()
cv2.destroyAllWindows()
