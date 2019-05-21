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

import sys

file = sys.argv[1]
print "要解析的文件：%s" % file

image = cv2.imread(file)
image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
thresh = filters.threshold_otsu(image) #自动探测一个阈值
print "thresh:",thresh

t =(image <= thresh)
cv2.imwrite("tmp.jpg",t*255)
image = Image.open('tmp.jpg')
code = pytesseract.image_to_string(image,lang='chi_sim',config="-psm 3")
print "结果："
print(code)
