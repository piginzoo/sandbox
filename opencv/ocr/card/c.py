# coding:utf8
# https://blog.csdn.net/qq_37674858/article/details/80624084
import sys

import cv2
import numpy as np
import pytesseract
from PIL import Image

def preprocess(gray):
    # 1. Sobel算子，x方向求梯度
    sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize = 3)
    # 2. 二值化
    ret, binary = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)

    # 3. 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 9))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 6))

    # 4. 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations = 1)

    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    erosion = cv2.erode(dilation, element1, iterations = 1)

    # 6. 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations = 4)


    # 7. 存储中间图片
    # cv2.imwrite("binary.png", binary)
    # cv2.imwrite("dilation.png", dilation)
    # cv2.imwrite("erosion.png", erosion)
    # cv2.imwrite("dilation2.png", dilation2)

    return dilation2


def findTextRegion(img):
    region = []

    # 1. 查找轮廓
    (_,contours,_)= cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 2. 筛选那些面积小的
    for i in range(len(contours)):
        cnt = contours[i]
        # 计算该轮廓的面积
        area = cv2.contourArea(cnt)

        # 面积小的都筛选掉
        if(area < 1000):
            continue

        # 轮廓近似，作用很小
        epsilon = 0.001 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # 找到最小的矩形，该矩形可能有方向
        rect = cv2.minAreaRect(cnt)
        # print("rect is: ")
        # print(rect)

        # box是四个点的坐标
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])

        # 筛选那些太细的矩形，留下扁的
        if(height > width * 1.2):
            continue

        region.append(box)

    return region


def detect(img):
    cut_img=[]
    # 1.  转化成灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('w',gray)
    # img_GaussianBlur = cv2.GaussianBlur(gray, (7, 7), 0)
    # sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    # sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    #
    # sobelx = np.uint8(np.absolute(sobelx))
    # sobely = np.uint8(np.absolute(sobely))
    # sobelcombine = cv2.bitwise_or(sobelx, sobely)
    # img_bilateralFilter = cv2.bilateralFilter(sobelcombine, 1, 75, 75)
    # dst = cv2.bilateralFilter(gray, 0, 100, 15)
    # cv2.imshow('g',dst)
    # cv2.waitKey()
    #
    #
    # # im_at_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5,10)  # 算术平法的自适应二值化
    # im_at_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 8) # 高斯加权均值法自适应二值化
    # # retval, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)  # 固定阈值二值化
    # cv2.imshow('w', im_at_mean)
    # cv2.waitKey()
    # img_medianBlur = cv2.medianBlur(gray, 5)
    # img_Blur = cv2.blur(gray, (5, 5))
    img_bilateralFilter = cv2.bilateralFilter(gray, 15, 50, 50)
    # img_Blur = cv2.blur(gray, (5, 5))
    # img_GaussianBlur = cv2.GaussianBlur(gray, (7, 7), 0)
    # img_medianBlur = cv2.medianBlur(gray, 5)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    #
    # # 开运算
    # opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    # # 显示腐蚀后的图像
    # cv2.imshow("Open", opened)
    # # 腐蚀图像
    # eroded = cv2.erode(gray, kernel)
    # # 显示腐蚀后的图像
    # cv2.imshow("Eroded Image", eroded)

    im_at_mean = cv2.adaptiveThreshold(img_bilateralFilter, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 5)  # 算术平法的自适应二值化
    cv2.imshow('pic2',im_at_mean)
    cv2.waitKey()

    ###########二值化算法

    # 2. 形态学变换的预处理，得到可以查找矩形的图片
    dilation = preprocess(im_at_mean)
    # cv2.imshow('2',dilation)
    # 3. 查找和筛选文字区域
    region = findTextRegion(dilation)
    # print(region)
    # 4. 用红线画出这些找到的轮廓
    for box in region:
        # cv2.drawContours(im_at_mean, [box], 0, (0, 0, 255), 2)

        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)
        hight = y2 - y1
        width = x2 - x1
        # print(hight,width)
        crop_img= im_at_mean[y1:y1 + hight, x1:x1 + width]
        # cv2.imshow('re',crop_img)
        # cv2.waitKey()
        code = pytesseract.image_to_string(crop_img, lang='chi_sim')

        print(code)










    # # # 带轮廓的图片
    # # cv2.imwrite("contours.png", img)
    #
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    # 读取文件

    img = cv2.imread('a.jpg')
    detect(img)
