#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from imutils.perspective import four_point_transform

img=cv2.imread('a.jpg')
# cv2.imshow('img',img)
# cv2.waitKey()
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #灰度处理
# cv2.imshow('gray',gray)
# cv2.waitKey()
blurred = cv2.GaussianBlur(gray, (5,5),0,0) #高斯滤波
# cv2.imshow('blurred',blurred)
# cv2.waitKey()
element=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))  # 获取自定义核 第一个参数MORPH_RECT表示矩形的卷积核，当然还可以选择椭圆形的、交叉型的
dilate = cv2.dilate(blurred,element) # 膨胀操作
# cv2.imshow('dilate',dilate)
# cv2.waitKey()
canny = cv2.Canny(dilate, 30, 130, 3)  # 边缘提取
cv2.imshow('canny',canny)
cv2.waitKey()

image, contours, hier = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #找轮廓
# 找出最大轮廓
max_area = 0
max_contour = 0
for contour in contours:
    tmparea = abs(cv2.contourArea(contour))
    if max_area < tmparea:
        max_area = tmparea
        max_contour = contour
# print(max_contour)
imge=cv2.drawContours(img.copy(),max_contour,-1,(0,0,255),3) #画出轮廓
# cv2.imshow('imge',imge)
# cv2.waitKey()

# 透视变化
rect = cv2.minAreaRect(max_contour)  #得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
# print(rect)
boxPoints=cv2.boxPoints(rect)   # cv2.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点

# 去掉边缘 取最小
for i in range(len(boxPoints)) :
    x1 = boxPoints[i][0]
    y1 = boxPoints[i][1]
    # print(x1,y1)
    min_distancey = 0
    for point in max_contour:
        distancey = abs(point[0][0] - x1) + abs(point[0][1] - y1)
        if min_distancey == 0 :
            min_distancey = distancey
        else :
            if distancey < min_distancey :
                min_distancey = distancey
                boxPoints[i] = point

fin=four_point_transform(img, boxPoints.reshape(4,2))
cv2.imshow('fin',fin)
cv2.waitKey()

cv2.imwrite('./out/fin.png',fin)