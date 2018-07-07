# coding: utf-8

import cv2
import numpy as np
imga = cv2.imread('data/a.jpg',cv2.IMREAD_GRAYSCALE)

print(imga.shape)


r,imga = cv2.threshold(imga,127,255,cv2.THRESH_BINARY_INV)  
cv2.imshow("raw",imga)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
#腐蚀图像
eroded = cv2.erode(imga,kernel)
#显示腐蚀后的图像
cv2.imshow("Eroded Image",eroded)
# #膨胀图像
dilated = cv2.dilate(eroded,kernel)
# #显示膨胀后的图像
cv2.imshow("Dilated Image",dilated)


pad = 1
rectangle = np.zeros(imga.shape, dtype = "uint8")
cv2.rectangle(rectangle, (pad,pad), (imga.shape[1]-2*pad, imga.shape[0]-2*pad), 255, -1)
cv2.imshow("Rectangle", rectangle)
masked = cv2.bitwise_and(imga, imga, mask=rectangle)
cv2.imshow("maksed",masked)




width = imga.shape[1]
height = imga.shape[0]
if width < 100:
	print("enlarge width")
	img = np.concatenate(
			(imga, np.zeros((height, 100 - width), dtype='uint8')), axis=1)
else:
	print("no change")
	img  = imga



if height < 100:
	print("enlarge width")
	img = np.concatenate(
			(img, np.zeros((100 - height, 100), dtype='uint8')), axis=0)
else:
	print("no change")


cv2.waitKey(0)
cv2.destroyAllWindows()




