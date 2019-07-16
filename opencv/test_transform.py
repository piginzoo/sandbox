import cv2


import cv2
import numpy as np
import matplotlib.pyplot as plt


# https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_core/py_image_arithmetics/py_image_arithmetics.html?highlight=saturate

bg_img = cv2.imread("background.png")
bg_img = cv2.cvtColor(bg_img,cv2.COLOR_BGR2BGRA)

img = cv2.imread("zoo2.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

h,w = img.shape[:2]
pts1 = np.float32([[0,0],[w,0],[0,h],[w,h]])
pts2 = np.float32([[100,0],[w-100,0],[0,h],[w,h]])
M = cv2.getPerspectiveTransform(pts1,pts2)


#第三个参数：变换后的图像大小
# white_image = np.zeros((h,w,3), np.uint8)
# white_image[:,:,:] = 
res = cv2.warpPerspective(img,M,(w,h))#,white_image,borderMode=cv2.BORDER_TRANSPARENT)
img2gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
mask_inv = cv2.bitwise_not(mask)
# Now black-out the area of logo in ROI
img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
# Take only region of logo from logo image.
img2_fg = cv2.bitwise_and(res,res,mask = mask)


res = cv2.cvtColor(res, cv2.COLOR_BGR2BGRA)
print(bg_img.shape)
print(res.shape)
# added_image = cv2.addWeighted(bg_img,0.4,res,0.1,0,res.shape)
# added_image = cv2.add(bg_img,res)
# added_image = cv2.add(bg_img,res)
cv2.imwrite("out/zoo2.png",added_image)

