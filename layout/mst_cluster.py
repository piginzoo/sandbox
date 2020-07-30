import bbox
import layout
import points_tool
import data_loader
import numpy as np
from row_parser import *


def cacluate_distance(row_elements):
    for e in row_elements:
        print(e)
    print("一行")


# 去探测他的value：
# 左面的框的右侧2点的y1,y2，右面的框的左侧2点的y1,y2
detect_pixs = 20  #


def detect_value(bboxes, poses, key_bbox):  # key_bbox[4,2]

    # sort_indexs = np.lexsort(key_bbox.T[:1,:])#
    # sorted_key_bboxes_by_x = key_bbox[sort_indexs,:] # 从小到大按照x排序
    # key_bbox_right_2_points = sorted_key_bboxes_by_x[2:] # key bboxes右侧2点

    print(key_bbox)
    max_y = np.max(key_bbox[:, 1])
    min_y = np.min(key_bbox[:, 1])

    print(poses.shape)
    candidate_poses = poses[np.where(poses[:,:,1] > min_y & poses[:,:,1] < max_y)]
    print(candidate_poses)


def process():
    images, all_poses, all_text, all_bboxes = data_loader.load_data("data")
    all_bboxes = all_bboxes[:1]

    for i in range(len(all_bboxes)):
        one_image_bboxes = all_bboxes[i]
        one_image_poses = all_poses[i]
        key_boxes = []
        for _bbox in one_image_bboxes:
            text = _bbox.txt
            field = bbox.find_similar_key(text)
            if field:
                logger.info("此bbox[%s]匹配文本为[%s]的key[%s]", text, field['text'], field['key'])
                bbox.field = field
                key_boxes.append(_bbox)

        # cacluate_distance(row_elements)

        for key_bbox in key_boxes:
            detect_value(one_image_bboxes, one_image_poses, key_bbox.pos)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                        handlers=[logging.StreamHandler()])
    process()
