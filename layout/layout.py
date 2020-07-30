import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool

# 处理一张图
def process(image, pos):
    logger.debug("此图bboxes们：%r", pos.shape)
    left_data, avarage_row_heigt, exclued_data = exclude_1sigma(pos)
    # [N,x,y]
    height = pos[:, :, 1].max()  # 所有bbox的最大的y
    width = pos[:, :, 0].max()  # 所有bbox的最大的x
    logger.debug("图像最高：%d", height)
    rows, row_elements = recognize_row(left_data, height)
    rows, row_elements = split_high_row(rows, row_elements, avarage_row_heigt)
    logger.debug("最终切分出%d行rows和%d行row_elements", len(rows), len(row_elements))

    image = debug(image, rows, width, pos, exclued_data, abnormal_data=None)
    return image


# TODO：矩形识别旋转的算法大bug

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    import layout
    images, raw_pos, all_text = layout.load_data("data")

    # 保留
    # original_pos = all_horizontal_pos.copy()

    for i in range(len(raw_pos)):

        one_image_horizontal_pos = []
        for pos in raw_pos[i]:
            rotated_pos = points_tool.rotate_rect_to_horizontal(pos)
            one_image_horizontal_pos.append(rotated_pos)
        one_image_pos = np.array(one_image_horizontal_pos)

        image = process(images[i], one_image_pos)

        # cv2.polylines(image, raw_pos[i], isClosed=True, color=(255, 0, 0), thickness=1)
        # cv2.polylines(image, one_image_pos, isClosed=True, color=(0, 0,255), thickness=1)
        # find_key_value(all_text[i],all_pos[i])
        print("--------------------------------------------------------")
        cv2.imwrite("debug/{}.jpg".format(i), image)
