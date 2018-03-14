# coding: utf-8
# 此文件用来测试type5类型的验证码的处理
import numpy as np
import cv2,os

def output_img(name,img):
	cv2.imwrite('out/'+name+'.jpg',img)

file_list = os.listdir("data/")

for file in file_list:
	imgname = "data/"+file
	print(imgname)
	img = cv2.imread(imgname, cv2.IMREAD_GRAYSCALE)
	retval, t = cv2.threshold(img, 240, 1, cv2.THRESH_BINARY_INV)
	output_img(file+"二值化",t*255)