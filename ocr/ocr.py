# coding: utf-8
# 此文件用来测试type5类型的验证码的处理
import numpy as np
import cv2,os
from skimage import color
import pytesseract,cv2
from PIL import Image
from skimage.measure import regionprops
from skimage import morphology,color,data,filters,io
from skimage.morphology import label,disk


img = cv2.imread('a.jpg')
image_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
thresh = filters.threshold_otsu(image_gray) #自动探测一个阈值
print "thresh:",thresh
t =(image_gray <= thresh)
cv2.imwrite("a_bw.jpg",t*255)
image = Image.open('a_bw.jpg')
code = pytesseract.image_to_string(image,lang='chi_sim',config="-psm 3")
print "正面："
print(code)
print "-----------------------------------------"
print "反面："

img = cv2.imread('b.jpg')
image_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
thresh = filters.threshold_otsu(image_gray) #自动探测一个阈值
print "thresh:",thresh
t =(image_gray <= thresh)
cv2.imwrite("b_bw.jpg",t*255)
image = Image.open('b_bw.jpg')
code = pytesseract.image_to_string(image,lang='chi_sim',config="-psm 1")
print code
