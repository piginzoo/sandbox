import numpy as np
import cv2

COLOR_BLACK=(0,0,0)
COLOR_RED=(0,0,255)
COLOR_GREEN=(0,255,0)
COLOR_BLUE=(255,0,0)
COLOR_YELLOW=(0,255,255)

def debug(image,rows,width,row_elements, exclued_data, abnormal_data):
    # 准备矩形框数据：[N,2] => [N,2，2]
    # [[y1,y2],...] => [[[10,y1],[790,y2]],...]
    rec_data = np.expand_dims(rows, axis=2)
    zeros = np.zeros(rec_data.shape)
    rec_data = np.concatenate((zeros, rec_data), axis=2)
    rec_data[:, 0, 0] = 10  # p1(10,y1)
    rec_data[:, 1, 0] = width - 10  # p1(width-10,y2)
    rec_data = np.int32(rec_data)
    overlay = image.copy()
    odd_row = True  # 奇数行

    for i in range(len(rec_data)):
        rec = rec_data[i]
        pos = row_elements[i]
        pos = np.int32(pos)
        p1 = tuple(rec[0].tolist())
        p2 = tuple(rec[1].tolist())
        print(pos)
        if odd_row:
            cv2.rectangle(overlay, p1, p2,COLOR_BLUE, -1)
            color = (100, 0, 0)
            cv2.polylines(image, pos, isClosed=True, color=color, thickness=1)
        else:
            cv2.rectangle(overlay, p1, p2, COLOR_GREEN, -1)
            cv2.polylines(image, pos, isClosed=True, color=COLOR_YELLOW, thickness=1)
        odd_row = bool(1 - odd_row)
    alpha = 0.4  # Transparency factor.
    image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    if exclued_data is not None:
        exclued_data = np.int32([exclued_data])
        for pos in exclued_data:
            cv2.polylines(image, pos, isClosed=True, color=COLOR_RED, thickness=1) # 异常框，红色

    if abnormal_data is not None:
        abnormal_data = np.int32([abnormal_data])
        for pos in abnormal_data:
            cv2.polylines(image, pos, isClosed=True, color=COLOR_BLACK, thickness=1)

    return image

# 把小框都画上
def draw_polys_with_color(image, polys, color):
    polys = [p for p in polys if not (p==0).all()]
    if len(polys) == 0: return
    polys = np.int32(polys)
    assert polys.shape[-2:]==(4,2), "实际shape:{}".format(polys.shape[-2:])
    for pos in polys:
        cv2.polylines(image, [pos], isClosed=True, color=color, thickness=2)

# 把小框都画上
def draw_poly_with_color(image, poly, color):
    poly = np.int32(poly)
    assert poly.shape[:2] == (4, 2), "实际shape:{}".format(poly.shape)
    cv2.polylines(image, [poly], isClosed=True, color=color, thickness=2)


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
def draw_rows(image, data):
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
