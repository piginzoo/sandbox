import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool
import table

# 处理一张图
def process(image, bboxes):
    logger.debug("开始处理此图的bboxes们：%d个", len(bboxes))

    for _bbox in bboxes:
        cv2.polylines(image,[_bbox.pos],True,COLOR_BLACK,thickness=1)

    bboxes,exclued_boxes = exclude_empty_text_bboxes(bboxes)

    good_boxes, bad_boxes, average_bbox_height, image_width, image_height = exclude_boxes_by_statistics(bboxes, sigma_num=2)

    exclued_boxes += bad_boxes

    all_rows, all_row_boxes = recognize_rough_row(good_boxes, image_height)

    all_row_boxes = split_high_rows_2(all_rows, all_row_boxes, average_bbox_height,image_width)

    logger.debug("最终切分出%d行all_rows和%d行all_row_boxes", len(all_rows), len(all_row_boxes))

    # 遍历每一行
    for i in range(len(all_row_boxes)):
        bboxes_of_row =  all_row_boxes[i]
        # 找出这一行的所有的bboxes
        key_counter = 0
        for _bbox in bboxes_of_row:
            field = bbox.find_similar_key(_bbox.txt, "table")
            if field:
                logger.debug("此bbox[%s]匹配文本为[%s]的key[%s]", _bbox.txt, field['text'], field['key'])
                _bbox.field = field  # <------- 把field，类似于meta放置入bbox肚子里
                key_counter += 1
        # 计算这行的bbox们，多少比例是key标题
        title_key_ratio = key_counter / len(bboxes_of_row)

        if title_key_ratio >= 0.5 and len(bboxes_of_row)>=3:
            logger.debug("这行有[%d]个标题，超过3个，60%%的标题都是key，我有理由相信他是表格标题行:",len(bboxes_of_row))

            __table = table.table_builder(bboxes_of_row,all_row_boxes[i+1:],average_bbox_height,image_width, image_height)
            logger.info("表格：")
            logger.info("=============================================================================================================================")
            logger.info("\t|\t".join([ str(header_bbox) for header_bbox in bboxes_of_row]))
            logger.info(str(__table))
            logger.info("=============================================================================================================================")
        else:
            logger.debug("此行[%d]个框,[%d]是潜在表标题,比例[%.2f]",len(bboxes_of_row),key_counter,title_key_ratio)

    image = debug(image, all_rows, all_row_boxes, exclued_boxes, image_width)
    return image


# TODO：矩形识别旋转的算法大bug

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    import data_loader

    image_names, images, all_poses, all_txt, all_bboxes = data_loader.load_data("data")

    # 保留
    # original_pos = all_horizontal_pos.copy()

    for i in range(len(all_bboxes)):
        # one_image_horizontal_pos = []
        # for pos in all_poses[i]:
        #     rotated_pos = points_tool.rotate_rect_to_horizontal(pos)
        #     one_image_horizontal_pos.append(rotated_pos)
        # one_image_poses = np.array(one_image_horizontal_pos)
        one_image_bboxes = all_bboxes[i]
        logger.info("========================================================")
        logger.info("    %s",image_names[i])
        logger.info("========================================================")
        image = process(images[i], one_image_bboxes)

        # cv2.polylines(image, all_pos[i], isClosed=True, color=(255, 0, 0), thickness=1)
        # cv2.polylines(image, one_image_pos, isClosed=True, color=(0, 0,255), thickness=1)
        # find_key_value(all_text[i],all_pos[i])
        print("--------------------------------------------------------")
        cv2.imwrite("debug/{}".format(image_names[i]), image)
