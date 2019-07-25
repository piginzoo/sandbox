import cv2,numpy as np
import matplotlib.pyplot as plt

 

def ocr(img_name):
	org_img = img = cv2.imread(img_name,0) #直接读为灰度图像

	cv2.imwrite('out/原图.jpg',org_img)

	# var kernal = Cv.CreateStructuringElementEx(5, 2, 1, 1, ElementShape.Rect);
	#             Cv.Erode(gray, gray, kernal, 2);
	kernel = np.ones((5,5),np.uint8)  
	img = cv2.erode(img,kernel,iterations = 1)            
	cv2.imwrite('out/膨胀.jpg',img)

	#简单滤波
	ret1,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
	cv2.imwrite('out/二值-127.jpg',th1)

	#Otsu 滤波
	ret2,th2 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	# print(th2)
	cv2.imwrite('out/二值-OTSU.jpg',th2)


	# https://blog.csdn.net/sunny2038/article/details/9170013
	img = th2
	x = cv2.Sobel(img,cv2.CV_16S,1,0)
	y = cv2.Sobel(img,cv2.CV_16S,0,1)
	absX = cv2.convertScaleAbs(x)# 转回uint8
	absY = cv2.convertScaleAbs(y) 
	dst = cv2.addWeighted(absX,0.5,absY,0.5,0)
	cv2.imwrite('out/X-Sebel滤波.jpg',absX)
	cv2.imwrite('out/Y-Sebel滤波.jpg',absY)
	cv2.imwrite('out/Sebel滤波边缘监测.jpg',dst)


	# 输出的返回值，image是原图像、contours是图像的轮廓、hier是层次类型
	# https://blog.csdn.net/HuangZhang_123/article/details/80511270
	img = dst
	black = cv2.cvtColor(np.zeros((img.shape[1], img.shape[0]), dtype=np.uint8), cv2.COLOR_GRAY2BGR)
	image, contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


	hulls = []
	for cnt in contours:
		# 轮廓周长也被称为弧长。可以使用函数 cv2.arcLength() 计算得到。这个函数的第二参数可以用来指定对象的形状是闭合的（True） ，还是打开的（一条曲线）
	    epsilon = 0.001 * cv2.arcLength(cnt, True)
		# 函数approxPolyDP来对指定的点集进行逼近，cnt是图像轮廓，epsilon表示的是精度，越小精度越高，因为表示的意思是是原始曲线与近似曲线之间的最大距离。
	    # 第三个函数参数若为true,则说明近似曲线是闭合的，它的首位都是相连，反之，若为false，则断开。
	    approx = cv2.approxPolyDP(cnt, epsilon, True)
	    # convexHull检查一个曲线的凸性缺陷并进行修正，参数cnt是图像轮廓。
	    hull = cv2.convexHull(cnt)
	    maxs = np.max(hull,axis=0)[0]
	    mins = np.min(hull,axis=0)[0]
	    hull= np.array([
	    	[mins[0],mins[1]],
	    	[maxs[0],mins[1]],
	    	[maxs[0],maxs[1]],
	    	[mins[0],maxs[1]]])
	    hulls.append(hull)

	    # # 勾画图像原始的轮廓
	    # cv2.drawContours(black, [cnt], -1, (0, 255, 0), 2)
	    # # 用多边形勾画轮廓区域
	    # cv2.drawContours(black, [approx], -1, (255, 255, 0), 2)
	    # 修正凸性缺陷的轮廓区域
	    cv2.drawContours(black, [hull], -1, (0, 0, 255), 2)
	    # print(hull.shape) [点数,1,2]
	# print(hulls)
	cv2.imwrite('out/文字探测结果.jpg',black)



	img = org_img
	img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR) 
	for rect in hulls:
		# print(rect.shape)
		cv2.polylines(img,[rect],True,(0,0,255))
	cv2.imwrite('out/最终探测结果.jpg',img)
	return img

def main():
	import os 

	g = os.walk("data")  

	for path,dir_list,file_list in g:  
		for file_name in file_list:  
			full_path = os.path.join(path, file_name)
			print(full_path)
			out_img = ocr(full_path)
			cv2.imwrite("output/"+file_name,out_img)

if __name__ == '__main__':
	import sys
	# print(len(sys.argv))
	if len(sys.argv)==2:
		file_name = sys.argv[1]
		print("处理单个文件：",file_name)
		ocr(file_name)
	else:
		print("处理目录")
		main()


