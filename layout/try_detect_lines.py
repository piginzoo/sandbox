import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool

# 处理一张图
def process(image, poses,txts):
    logger.debug("此图bboxes们：%r", poses.shape)
    exclued_data=[]
    new_poses = []
    for i in range(len(txts)):
        if txts[i].strip()=="":
            logger.debug("此框识别文字为空，怒弃")
            exclued_data.append(poses[i])
        else:
            new_poses.append(poses[i])

    left_data, avarage_row_heigt, __exclued_data = exclude_1sigma(new_poses,sigma_num=2)
    exclued_data+=__exclued_data

    # [N,x,y]
    height = poses[:, :, 1].max()  # 所有bbox的最大的y
    width = poses[:, :, 0].max()  # 所有bbox的最大的x
    logger.debug("图像最高：%d", height)
    rows, row_elements = recognize_row(left_data, height)

    # rows, row_elements = split_high_row(rows, row_elements, avarage_row_heigt)
    # logger.debug("最终切分出%d行rows和%d行row_elements", len(rows), len(row_elements))

    image = debug(image, rows, width, row_elements, exclued_data, abnormal_data=None)
    return image


# TODO：矩形识别旋转的算法大bug

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    import data_loader
    image_names, images, all_poses, all_txt, all_bboxes= data_loader.load_data("data")

    # 保留
    # original_pos = all_horizontal_pos.copy()

    for i in range(len(all_poses)):

        # one_image_horizontal_pos = []
        # for pos in all_poses[i]:
        #     rotated_pos = points_tool.rotate_rect_to_horizontal(pos)
        #     one_image_horizontal_pos.append(rotated_pos)
        # one_image_poses = np.array(one_image_horizontal_pos)
        one_image_poses = all_poses[i]

        image = process(images[i], one_image_poses,all_txt[i])

        # cv2.polylines(image, all_pos[i], isClosed=True, color=(255, 0, 0), thickness=1)
        # cv2.polylines(image, one_image_pos, isClosed=True, color=(0, 0,255), thickness=1)
        # find_key_value(all_text[i],all_pos[i])
        print("--------------------------------------------------------")
        cv2.imwrite("debug/{}".format(image_names[i]), image)
