# coding: utf-8

import cv2
import numpy
img = cv2.imread('test.jpg')
print img
print (img.shape)
print img.dtype

px=img[10,10]
print(px)
blue = img[10,10,2]
print(blue)
print (type(blue))
print(img.item(10,10,2))
img[11,11]=[255,0,0]
print(img[11,11])
#cv2.imwrite('out/imgoperation_out.jpg',img)

#测试ROI（region of interesting）
img = cv2.imread('test.jpg')
part = img [20:20,60:60]
img[40:40,80:80]= part
cv2.imshow("[roiImg]",img)
#cv2.waitKey(0)
#cv2.imwrite('out/imgoperation_out.jpg',img) 

#把BGR的R（索引是2），全部置0
img = cv2.imread('test.jpg')
img[:,:,2]= 0
#cv2.imwrite('out/imgoperation_out.jpg',img) 

#两张图融合到一起
img1 = cv2.imread('test.jpg')
img2 = cv2.imread('test2.jpg')
img = cv2.addWeighted(img1,0.3,img2,0.7,0)
cv2.imshow('2 pics',img)
cv2.waitKey(0)
cv2.destroyAllWindows()




