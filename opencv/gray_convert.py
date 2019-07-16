# coding: utf-8
# 此文件用来测试type5类型的验证码的处理
import numpy as np
import cv2,os
from skimage import color

def output_img(name,img):
	cv2.imwrite('out/'+name+'.jpg',img)

file_list = os.listdir("data/")

for file in file_list:
	imgname = "data/"+file
	print(imgname)
	img = cv2.imread(imgname)
	#这个方法不靠谱
	#image_gray = color.rgb2gray(img)
	image_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	output_img(file+"灰度化",image_gray)