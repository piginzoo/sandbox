# coding: utf-8
# 此文件用来测试type5类型的验证码的处理
import numpy as np
import cv2

def output_img(name,img):
	cv2.imwrite('out/train5_'+name+'.jpg',img)

imgname = "type5/type5_train_1.png"
img = cv2.imread(imgname, cv2.IMREAD_GRAYSCALE)
print "img shape:",img.shape
#print len(img)
#for row in img:
#	print row

#cv2.imshow(imgname,img)
#cv2.waitKey(0)

# 选取一个全局阈值，然后就把整幅图像分成了非黑即白的二值图像了
# 这个函数有四个参数，第一个原图像，第二个进行分类的阈值，
# 第三个是高于（低于）阈值时赋予的新值，第四个是一个方法选择参数，常用的有： 
# • cv2.THRESH_BINARY（黑白二值） 
# • cv2.THRESH_BINARY_INV（黑白二值反转） 
# 该函数有两个返回值，
# 第一个retVal（得到的阈值值（在后面一个方法中会用到）），
# 第二个就是阈值化后的图像。 
retval, t = cv2.threshold(img, 127, 1, cv2.THRESH_BINARY_INV)
#cv2.imshow("t",t)
#cv2.waitKey(0)
#===>把图像给二值化了，做了黑白反转，阈值是127，凡是低于阈值的都设为1
#debug了一下，就是把原来白的都变黑为0（靠THRESH_BINARY_INV这个参数），
#            然后原来黑的地方都变成1
print "做了阈值二值化处理的",t,"/",t.shape
output_img("binary_inv_img",t)
for row in t:
	print row

s = t.sum(axis=0)#210x64 ==> 210，降维，但是汇总了
print "s.size",len(s) 
print "二值化图像按列sum - s(是个图像数组):",s
#median：中位数，nonzeros(a)返回数组a中值不为零的元素的下标
y1 = (s > np.median(s) + 5).nonzero()[0][0]
print "s>np.median(s):",s>np.median(s)
print "(s > np.median(s) + 5)",(s > np.median(s) + 5)
print "(s > np.median(s) + 5).nonzero()",(s > np.median(s)+5).nonzero()
print "y1:",y1

#折腾这一圈，我理解是为了去掉横线，所以np.median(s) + 5的5，我理解就是线粗

y2 = (s > np.median(s) + 5).nonzero()[0][-1]
x1, x2 = 0, 36
#img数组的分片很诡异，不是x1:y1,x2:y2，
#而是这里写的x1:x2, y1:y2
#所以，这里作者认为识别码的竖着的方向，也就是x方向是0，36，说白了就是竖着36个像素
#而，x，y方向和我们的理解的是一致的，但是numpy表示是反的
#numpy表示的图像，高度（y坐标）在前，宽度（x坐标）在后
#所以这个img[x1:x2...]的x1,x2其实是y1,y2，就是图像的高度
im = img[x1:x2, y1 - 2:y2 + 3]
print "im:",im.shape,im
print "x1:y2,x1:y2:",x1,":",y1,",",x2,":",y2
output_img("cut_out_img",im)
#cv2.imshow("2 values",im)
#cv2.waitKey(0)

#再黑白颠倒一下
retval, im = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY_INV)
im0 = im[x1:x2, 1:-1]
print "im0:",im0.shape,im0
output_img("cut_out_inv_img",im0)
#cv2.imshow("im0",im0)
#cv2.waitKey(0)

#把宽度撑成了100个像素
if im.shape[1] < 100:
    im = np.concatenate((im, np.zeros((36, 100 - im.shape[1]), dtype='uint8')), axis=1)
else:
    im = cv2.resize(im, (100, 36))
print "new im:",im.shape,im
output_img("width_100_img",im)

I = im > 127 #得到一个是不是白的100x36的二维布尔矩阵，白的为true，黑的为false
print "I:",I.shape,I
#变成一个四维numpy.ndarray,为了和[图片个数？,image channel,height,width]
I = I.astype(np.float32).reshape((1, 1, 36, 100)) 
print "I:",I.shape,type(I),I

# n = nb_model.predict_classes(I, verbose=0) + 4
# im1 = np.zeros((36, 150), dtype=np.uint8)
# im1[:, 10:im0.shape[1] + 10] = im0
# step = im0.shape[1] / float(n)
# center = [i + step / 2 for i in np.arange(0, im0.shape[1], step).tolist()]
# imgs = np.zeros((n, 1, 36, 20), dtype=np.float32)
# for i, c in enumerate(center):
#     imgs[i, 0, :, :] = im1[:, c:c + 20]

#classes = chars_model.predict_classes(imgs.astype('float32') / 255.0, verbose=0)
#result = []
#for c in classes:
#     result.append(letters[c])
# print(name, ''.join(result).upper())
# f_csv.write(name + ',' + ''.join(result).upper() + '\n')

