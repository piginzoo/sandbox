#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

# 把一个过高的行分割成多行
def split_high_row(rows,row_elements,row_avarage_height):
    logger.debug("一共%d行，行均高mean+1std:%f" % (len(rows),row_avarage_height))


    # 确定行高，通过小框门的均值+2sigma

    # 看返回的行的行高和这个均高的误差，如果超过2倍，就认为是2行重叠了，就要分拆
    # 分拆的算法：
    #   先要规定什么叫1行，我们认为是1.5倍的（均值+2sigma）是一个合理的行高
    #   确定了行高就好办了，就挨个把每个框归队即可
    #   行的起始Y是框们的左上角排序后，第一个框的左上角Y值
    #   只要这个框的左上角在范围内，就收纳之，归队！

    new_rows_elements = []
    new_rows = []

    LINE_RATIO = 1

    for i in range(rows.shape[0]):
        row = rows[i]

        # 得到这行的行高
        row_height = abs(row[1] - row[0])

        # 如果这行在标准差的2倍以内，就认为是正常行，不处理
        if row_height< LINE_RATIO*row_avarage_height:
            new_rows.append(row)
            new_rows_elements.append(row_elements[i])
            logger.debug("此行高[%f]在%f倍均高[%f]内，属于正常行" , row_height, LINE_RATIO, LINE_RATIO*row_avarage_height)
            continue

        logger.debug("此行高[%f]超预定义行高[%f]，需要分拆..." % (row_height,LINE_RATIO*row_avarage_height))

        polys = row_elements[i]
        logger.debug("此行目前包含一共[%d]个bbox", len(polys))

        # 按左上角排序,从小到大，返回的是一个list，不是numpy？
        sorted_polys=sorted(polys, key=lambda x:x[:, 1].min())

        logger.debug("先对行内小框们按照左上角坐标排序")

        new_row_height = LINE_RATIO*row_avarage_height #<------------------------------------------------ 这个是最关键的，确定行高
        logger.debug("定义新行高[%f]",new_row_height)

        left_polys_of_row = sorted_polys
        while(len(left_polys_of_row)!=0):

            #得到新行的起始位置，就是最靠上poly(也就是第一个)的左上角坐标,[4,2]
            new_row_y1 = left_polys_of_row[0][:,1].min()# 4点里的最小y值
            new_row_y2 = new_row_y1 +  new_row_height
            logger.debug("确定新行的y1:%d,y2:%d" %(new_row_y1,new_row_y2))

            # 然后用新的y1,y2去过滤小框们，形成一个新行，直到处理完毕
            new_poloys_of_row = []
            exclude_poloys_of_row = []

            # 遍历剩下的bbox，看看他的最下面(最大的y)是否在新行内，如果在，加入到新行
            for poly in left_polys_of_row:
                p_y1 = poly[:, 1].min()
                p_y2 = poly[:,1].max()
                # 如果点的左下角的y值，小于新行的下沿，就并入此行
                if p_y2<=new_row_y2:
                    logger.debug("此bbox框在新行的内，加入新行集合")
                    new_poloys_of_row.append(poly)
                    continue

                if new_row_y2 - p_y1 > row_avarage_height/2:
                    logger.debug("此bbox框的一般在新行的内，加入新行集合")
                    new_poloys_of_row.append(poly)
                    continue

                logger.debug("此bbox框无法归入新定义行，等待加入下一行")
                exclude_poloys_of_row.append(poly)


            new_row = [new_row_y1,new_row_y2]
            new_rows.append(new_row)
            new_rows_elements.append(new_poloys_of_row)
            logger.debug("%d个小框加入新行%r" % (len(new_poloys_of_row),new_row))

            # 剔除已经归队的小框门，继续这个过程，直到为空
            left_polys_of_row = exclude_poloys_of_row
            logger.debug("排序的原有行的小框数量剩余：%d,剔除: %d" %(len(left_polys_of_row),len(new_poloys_of_row)) )

    return new_rows,new_rows_elements

# 剔除一个标准差之外的数据
# raw_data,原始数据[N,4,2] : [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
def exclude_1sigma(raw_data):

    # 把[N,4,2]变成[N],里面放着每个框的高度
    data = np.array(raw_data)
    data = np.array(data[:,:8],np.float)
    data = data.reshape(-1, 4, 2)
    heights = data[:, :, 1].max(axis=1) - data[:, :, 1].min(axis=1)

    std = heights.std()
    max = heights.max()
    min = heights.min()
    mean = heights.mean()
    logger.debug("数据情况：mean={},std={},max={},min={}".format(mean,std,max,min))

    max_height = mean + std
    min_height = mean - std
    logger.debug("2个标准差下，最大高度为：%f，最小高度为：%f",max_height,min_height)

    bad_heights_indices = np.where(np.logical_or(heights > max_height,heights < min_height))
    bad = [raw_data[i] for i in bad_heights_indices[0]]

    good_heights_indices = np.where(np.logical_and(heights <= max_height,heights >= min_height))
    good = [raw_data[i] for i in good_heights_indices[0]]

    logger.debug("一共有%d个框，正常框[%d]个，异常框框[%d]",len(heights),len(good),len(bad))
    return good,mean,bad



# 输入：是图片高度，和小框们
# 输出：每一个行的起始和终止Y值，如：[[0,15],[28,35],...]
# 这个方法，只是看投影，只要有投影，就说明还是在一个大的行内，所以，他的问题是，可能会切割出很高的行
# 高行会在后面处理
def recognize_row(data,image_height):

    logger.debug("进行行识别，数据:%r，图像高度：%d",len(data),image_height)
    h_array = np.zeros(image_height, dtype=np.int32)

    # 先都往y轴上做投影
    for poly in data: # 一个框
        poly = poly[:8] # 去除文本
        poly = np.array(poly,np.float).astype(np.int32)
        poly = poly.reshape(4,2)
        y1 = poly[:,1].min()
        y2 = poly[:,1].max()
        # 向Y轴做投影
        h_array[y1:y2] = 1

    pre_value = 0
    rows = []

    # 从0跃迁到1的连续区间，记录其开始、结束为止，即投影线段，h_array是一个图像高为长度的一个0/1数组
    for i,value in enumerate(h_array.tolist()):
        if  pre_value == 0 and value == 1:
            rows.append(i)
        if  pre_value == 1 and value == 0:
            rows.append(i)
        pre_value = value
    logger.debug("先做行投影找到连续行%d个",len(rows))

    # 让最后的点是偶数
    if len(rows) % 2 != 0:
        # logger.debug("行[%d]y1y2需为偶数，增加一行",len(rows))
        rows.append(image_height)

    rows = np.array(rows)
    rows = rows.reshape(-1,2)

    # 每个框都归队
    row_elements = []
    for row in rows:
        one_row_elements = []

        remove_index = []
        # logger.debug("处理一行：%r",row)
        for d in data:  # 一个框

            poly = d[:8]
            poly = np.array(poly, np.float).astype(np.int32)
            poly = poly.reshape(4, 2)
            y1 = poly[0, 1]
            y2 = poly[3, 1]

            # 如果这个框的投影在某个行内，就归队到这行，然后在总集合中剔除他
            if y1>=row[0] and y2<=row[1]:
                logger.debug("框投影在行内：y1[%d]>=row_y1[%d],y2[%d]<=row_y2[%d]:", y1, y2, row[0], row[1])
                one_row_elements.append(d)
                # logger.debug("这个框的投影在行内，归队TA，并在总集合中剔除他:y1(%d)>row_y1(%d),y2(%d)<row_y2(%d)" % (y1,row[0],y2,row[1]))
        row_elements.append(one_row_elements)

    # rows和row_elements行数是一样的，对应行就是对应的框们
    logger.debug("识别出%d行",len(row_elements))
    return rows,row_elements

#../ctpn/data/train/labels/2019040107140584812123234.txt
# data shape是[N,9],前8个是坐标，最后一个是文本
def process(image_shape,data):

    left_data,avarage_row_heigt,exclued_data = exclude_1sigma(data)
    logger.debug("%d个正常框，%d个问题框（超过1sigma）",len(left_data),len(exclued_data))

    height,width,_ = image_shape
    rows,row_elements = recognize_row(left_data,height)
    rows, row_elements = split_high_row(rows,row_elements,avarage_row_heigt)
    logger.debug("最终切分出%d行rows和%d行row_elements",len(rows),len(row_elements))

    # rows_elements包含着正常的在行内的框
    # excluded_data包含着不包含在行内的框
    # abnromal_data包含着文本上异常的框：空串或者啥
    return rows, row_elements,exclued_data, abnormal_data


if __name__ == '__main__':

    #path = "../ctpn/data/train/labels/2019040107140584812123234.txt"
    path = "../data/vehicle/labels/27614.txt"
    f = open(path,"r",encoding='utf-8')
    lines = f.readlines()
    # logger.debug(lines)

    # from test import test_vehicle_recoginze
    # data = test_vehicle_recoginze.text_line_to_list(lines)

    data = []
    #190.0,276.0,477.0,276.0,477.0,293.0,190.0,293.0
    for line in lines:
        cord = []
        cords = line.split(",")
        cord = [ float(c) for c in cords[:8]]
        #cord = [int(c) for c in cords[:8]]
        #cord += cords[8:]
        data.append(cord)

    data = np.array(data)
    data.astype(int)

    image = cv2.imread("../data/vehicle/images/27614.jpg")

    rows, row_elements, exclued_data, abnormal_data = process(image.shape,data)


    _,width,_ =image.shape

    # 准备矩形框数据：[N,2] => [N,2，2]
    # [[y1,y2],...] => [[[10,y1],[790,y2]],...]
    rec_data = np.expand_dims(rows, axis=2)
    zeros = np.zeros(rec_data.shape)
    rec_data = np.concatenate((zeros,rec_data),axis=2)
    rec_data[:, 0, 0] = 10  # p1(10,y1)
    rec_data[:, 1, 0] = width - 10  # p1(width-10,y2)
    # ocr_utils.draw_rectange(image,rec_data)

    # 把小框画上去
    # ocr_utils.draw_poly(image, data ,exclued_data, abnormal_data)
