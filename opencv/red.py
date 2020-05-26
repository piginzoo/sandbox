# coding: utf-8
# 此文件用来测试type5类型的验证码的处理
import numpy as np
import skimage 
from skimage import io
import cv2

def output_img(name,img):
	cv2.imwrite('out/yin_'+name+'.jpg',img)

imgname = "red.jpg"
img = cv2.imread(imgname)
#img = io.imread(imgname)
print "img shape:",img.shape

cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
mask1 = cv2.inRange(hsv,(160,50,50),(180,255,255))
mask2 = cv2.inRange(hsv,(0,50,50),(8,255,255))
mask = cv2.bitwise_or(mask1, mask2)
res = cv2.bitwise_and(img,img,mask=mask)
# green_image = img.copy() # Make a copy
# green_image[:,:,0] = 0
# green_image[:,:,1] = 0

gray = cv2.cvtColor(green_image, cv2.COLOR_BGR2GRAY)

thresh  = gray>0

output_img("res",res)
output_img("bw",thresh*255)

