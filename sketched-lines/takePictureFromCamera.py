import numpy as np
import cv2
import os
#~ import subprocess
from sys import platform
	
def getFreeFilename():
	filenameNumber = 1
	getFilename = lambda: os.getcwd()+"/"+"photo"+str(filenameNumber).zfill(3)+".jpg"
	while os.path.isfile(getFilename()):
		filenameNumber += 1
	return getFilename()

def takeNewPhotoFromCamera():
	file=getFreeFilename()
	print "trying to capture: "+file
	if platform == "darwin": # on MAC, kill processes that take possession of camera
		os.system("killall PTPCamera")
	os.system("gphoto2 --capture-image-and-download --filename="+file)
	#~ process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	#~ bashOut = process.communicate()[0]
	#~ print bashOut
	assert os.path.isfile(file)
	return file

def showImage(file):
	img = cv2.imread(takeNewPhotoFromCamera())
	#~ img = cv2.imread("photo001.jpg")
	winName = "image"
	cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
	#~ cv2.resizeWindow(winName, 900, 600)
	#~ cv2.moveWindow(winName, 100, 100)
	cv2.imshow(winName, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

takeNewPhotoFromCamera()
