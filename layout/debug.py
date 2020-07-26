import numpy as np
import cv2

def debug(image,rows,width,data, exclued_data, abnormal_data):
    # 准备矩形框数据：[N,2] => [N,2，2]
    # [[y1,y2],...] => [[[10,y1],[790,y2]],...]
    rec_data = np.expand_dims(rows, axis=2)
    zeros = np.zeros(rec_data.shape)
    rec_data = np.concatenate((zeros, rec_data), axis=2)
    rec_data[:, 0, 0] = 10  # p1(10,y1)
    rec_data[:, 1, 0] = width - 10  # p1(width-10,y2)
    image = draw_rectange(image, rec_data)

    # 把小框画上去
    image = draw_poly(image, data, exclued_data, abnormal_data)

    return image


# 把小框都画上
def draw_poly(image, data, exclued_data=None, abnormal_data=None):
    data = np.int32([data])
    for pos in data:
        cv2.polylines(image, pos, isClosed=True, color=(255,0,0), thickness=1) #正常框，蓝色

    if exclued_data is not None:
        exclued_data = np.int32([exclued_data])
        for pos in exclued_data:
            cv2.polylines(image, pos, isClosed=True, color=(0,0,255), thickness=1) # 异常框，红色

    if abnormal_data is not None:
        abnormal_data = np.int32([abnormal_data])
        for pos in abnormal_data:
            cv2.polylines(image, pos, isClosed=True, color=(0, 0, 0), thickness=1)

    return image


# 画矩形框，填充，透明
def draw_rectange(image, data):
    data = np.int32(data)
    overlay = image.copy()
    odd_row = True  # 奇数行
    for rec in data:
        p1 = tuple(rec[0].tolist())
        p2 = tuple(rec[1].tolist())
        if odd_row:
            cv2.rectangle(overlay, p1, p2, (255, 0, 0), -1)
        else:
            cv2.rectangle(overlay, p1, p2, (0, 255, 0), -1)
        odd_row = bool(1 - odd_row)
    alpha = 0.4  # Transparency factor.
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
