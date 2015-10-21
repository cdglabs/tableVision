import numpy as np
import cv2
import os
from sys import platform
	
def getFreeFilename():
	filenameNumber = 1
	getFilename = lambda: os.getcwd()+"/"+"photo"+str(filenameNumber).zfill(3)+".jpg"
	while os.path.isfile(getFilename()):
		filenameNumber += 1
	return getFilename()

def takePictureFromCamera():
	file=getFreeFilename()
	print "trying to capture: "+file
	if platform == "darwin": # on MAC, kill processes that take possession of camera
		os.system("killall PTPCamera")
	os.system("gphoto2 --capture-image-and-download --filename="+file)
	assert os.path.isfile(file)
	return file

takePictureFromCamera()
