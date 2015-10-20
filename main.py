import cv2
import numm3

print 'Hello, world!'

gen = numm3.webcam_frames("/dev/video1", preamble=["-r", "30", "-s", "1280x720"])

numm3.run("main.numm.py", globals(), size=(1280, 720))
