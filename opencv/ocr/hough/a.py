# 先通过hough transform检测图片中的图片，计算直线的倾斜角度并实现对图片的旋转
# https://www.cnblogs.com/luofeel/p/9150968.html
import os
import cv2
import math
import random
import numpy as np
from scipy import misc, ndimage


img = cv2.imread('../data/card.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,50,150,apertureSize = 3)

print("edges.shape:",edges.shape)
misc.imsave('out/边缘.jpg',edges)

#霍夫变换
minLineLength = 500 # 最小直线长度，太小舍去
maxLineGap = 1 # 最大线段间隙， 太大舍去
lines = cv2.HoughLines(edges,1,np.pi/180,100,minLineLength, maxLineGap)
print(lines)
print(lines[1])
print(lines.shape)
lines = lines[:3]
for line in lines:
	for rho,theta in line:
	    a = np.cos(theta)
	    b = np.sin(theta)
	    x0 = a*rho
	    y0 = b*rho
	    x1 = int(x0 + 1000*(-b))
	    y1 = int(y0 + 1000*(a))
	    x2 = int(x0 - 1000*(-b))
	    y2 = int(y0 - 1000*(a))
	    print(x0,y0,x1,y1,x2,y2)
	    cv2.line(edges,(x1,y1),(x2,y2),(255,255,255),1)
misc.imsave('out/边缘线.jpg',edges)    
if x1 == x2 or y1 == y2:
	print("errror")
	exit(0)
t = float(y2-y1)/(x2-x1)
rotate_angle = math.degrees(math.atan(t))
if rotate_angle > 45:
	rotate_angle = -90 + rotate_angle
elif rotate_angle < -45:
	rotate_angle = 90 + rotate_angle
rotate_img = ndimage.rotate(img, rotate_angle)
misc.imsave('out/结果.jpg',rotate_img)