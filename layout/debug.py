import cv2
import logging
import numpy as np

logger = logging.getLogger(__name__)

COLOR_BLACK = (0, 0, 0)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)


def debug(image, all_rows, all_row_bboxs, exclued_bboxes, image_width):
    odd_row = True
    for i in range(len(all_row_bboxs)):  # 所有行
        one_row_bboxes = all_row_bboxs[i]

        one_row_bboxes = sorted(one_row_bboxes, key=lambda _bbox: _bbox.pos[:, 0].min())
        one_row_bbox_centers = [_bbox.center() for _bbox in one_row_bboxes]

        if odd_row:
            color = COLOR_BLUE
        else:
            color = COLOR_GREEN

        # logger.debug("打印行：此行%d个bbox", len(one_row_bboxes))
        for __bbox in one_row_bboxes:
            cv2.polylines(image, [__bbox.pos], isClosed=True, color=color, thickness=2)
        if len(one_row_bbox_centers) > 1:
            for i in range(len(one_row_bbox_centers) - 1):
                p1 = one_row_bbox_centers[i]
                p2 = one_row_bbox_centers[i + 1]
                cv2.line(image, p1, p2, color, thickness=2)

        odd_row = bool(1 - odd_row)

    if all_rows is not None:
        overlay = image.copy()
        all_rows = np.array(all_rows, np.int32)
        for row in all_rows:  # row=[y1,y2]
            y1 = min(row)
            y2 = max(row)
            overlay = cv2.rectangle(overlay, (10, y1), (image_width - 20, y2), COLOR_YELLOW, -1)
        alpha = 0.1  # Transparency factor.
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    if exclued_bboxes  is not None:
        for __box in exclued_bboxes:
            cv2.polylines(image, [__box.pos], isClosed=True, color=COLOR_RED, thickness=1)  # 异常框，红色

    return image


# 把小框都画上
def draw_polys_with_color(image, polys, color):
    polys = [p for p in polys if not (p == 0).all()]
    if len(polys) == 0: return
    polys = np.int32(polys)
    assert polys.shape[-2:] == (4, 2), "实际shape:{}".format(polys.shape[-2:])
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
        cv2.polylines(image, pos, isClosed=True, color=(255, 0, 0), thickness=1)  # 正常框，蓝色

    if exclued_data is not None:
        exclued_data = np.int32([exclued_data])
        for pos in exclued_data:
            cv2.polylines(image, pos, isClosed=True, color=(0, 0, 255), thickness=1)  # 异常框，红色

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
