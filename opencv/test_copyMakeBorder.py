import numpy as np
import cv2


def getPatches(img):
	h, w = img.shape[:2]
	# 扩充边界：copyMakeBorder(img,top,bottom,left,right,borderType,colar
	img = cv2.copyMakeBorder(img,  0,h     , 0  ,  w  ,cv2.BORDER_CONSTANT, value=(255,255,255))
	cv2.imshow("",img)
	cv2.waitKey(0)


getPatches(cv2.imread("logo.jpg"))
