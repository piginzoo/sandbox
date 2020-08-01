import bbox
import debug
import data_loader
from row_parser import *


def cacluate_distance(row_elements):
    for e in row_elements:
        print(e)
    print("一行")


# 去探测他的value：
# 左面的框的右侧2点的y1,y2，右面的框的左侧2点的y1,y2
def detect_value(bboxes, key_bbox):  # key_bbox[4,2]

    # 按照x的顺序，对bbox进行排序，这个只能用lexsort实现
    # sort_indexs = np.lexsort(key_bbox.T[:1,:])
    # sorted_key_bboxes_by_x = key_bbox[sort_indexs,:] # 从小到大按照x排序
    # key_bbox_right_2_points = sorted_key_bboxes_by_x[2:] # key bboxes右侧2点

    logger.debug("!!!开始分析Key[%r]",key_bbox)
    poses = bbox.get_poses(bboxes)

    # 过滤出任何一个点在 key_bbox的向右的辐射范围内，即目标bbox的任意一个点的y在key_bbox的最大y最小y的"上下"之间
    key_pos = key_bbox.pos
    max_y = np.max(key_pos[:, 1])
    min_y = np.min(key_pos[:, 1])
    larger_indexes = (poses[:, :, 1] > min_y).any(axis=1)
    less_indexes = (poses[:, :, 1] < max_y).any(axis=1)
    poses_left = poses[larger_indexes & less_indexes]
    logger.debug("此Key[%r]同行过滤后，剩余框(%d个)[%r]",key_bbox,len(poses_left),bbox.filter_bboxes_by_poses(bboxes,poses_left))

    # 再继续过滤，所有的备选框，都应该在key的右侧
    key_x = np.min(key_pos[:, 0])
    right_indexes = (poses_left[:, :, 0] > key_x).any(axis=1)
    poses_left = poses_left[right_indexes]
    logger.debug("此Key[%r]再过滤掉左面的，剩余框(%d个)[%r]",key_bbox,len(poses_left),bbox.filter_bboxes_by_poses(bboxes,poses_left))

    # [N,4,2], 按照最左面的x坐标排序
    poses_left = sorted(poses_left, key=lambda x: x[:, 0].min())

    target_value_boxes=[]
    for pos in poses_left:
        _bbox = bbox.find_bbox_by_pos(bboxes, pos)
        if _bbox is None:
            logger.debug("无法通过pos[%r]找到对应bbox", pos)
            continue
        logger.debug("!尝试分析此bbox[%r]....",_bbox)
        if _bbox == key_bbox:
            logger.debug("此框是我自己啊")
            continue  # 排除自己
        ratio=_bbox.vertical_overlay_ratio(key_bbox)
        if ratio<0.5:
            logger.debug("此框[%r]和key_bbox相交比不达标[%f]，忽略", _bbox,ratio)
            continue
        if _bbox.is_keybbox(): # 如果遇到了下一个key_bbox，那么就结束了
            logger.debug("遇到下一个key[%r]，value截止", _bbox)
            break

        logger.debug("找到value（挨着我的第一个）：%r,距离我：%d", _bbox, key_bbox.horizontal_distance(_bbox))
        target_value_boxes.append(_bbox)
    return target_value_boxes


def process():
    image_names, images, all_poses, all_text, all_bboxes = data_loader.load_data("data")
    # all_bboxes = all_bboxes[:1]


    for i in range(len(all_bboxes)):
        logger.info("==================================================================")
        logger.info("  处理图片：%s", image_names[i])
        logger.info("==================================================================")

        one_image_bboxes = all_bboxes[i]
        key_values = []  # 所有的key：value对，1：N的关系，可能有多个value bboxes

        bad_boxes = exclude_empty_text_bboxes(one_image_bboxes)
        good_boxes, __bad_boxes, mean = exclude_boxes_by_statistics(one_image_bboxes, sigma_num=2)
        bad_boxes+=__bad_boxes
        one_image_bboxes=good_boxes

        # 找出所有的key bboxes
        for _bbox in one_image_bboxes:
            text = _bbox.txt
            field = bbox.find_similar_key(text)
            if field:
                logger.debug("此bbox[%s]匹配文本为[%s]的key[%s]", text, field['text'], field['key'])
                _bbox.field = field  # <------- 把field，类似于meta放置入bbox肚子里
                key_values.append(bbox.KeyValue(_bbox))

        # TODO：删除掉，应该是不需要，因为后面还要用这些key
        # # 先统一从原有bboxes集合中删除所有key，排除一些干扰
        # for key_value in key_values:
        #     one_image_bboxes.remove(key_value.key_bbox)  # 把key_bboxes从原始的bboxes集合中都删除掉

        for key_value in key_values:
            key_bbox = key_value.key_bbox
            logger.debug("处理其中的一个key：%s", key_bbox.txt)

            value_bboxes = detect_value(one_image_bboxes, key_bbox)
            if len(value_bboxes)==0:
                logger.debug("无法为它找到value")
                continue

            logger.debug("!!!找到Key：%s ==> Value: %r", key_bbox.txt, value_bboxes)

            key_value.value_boxes+=value_bboxes
            for vb in value_bboxes:
                one_image_bboxes.remove(vb)  # 把这个value_bbox从原始的bboxes集合中都删除掉

        image = images[i]
        for key_value in key_values:
            key_pos = key_value.key_bbox.pos
            debug.draw_poly_with_color(image, key_pos, debug.COLOR_RED)

            value_poses = []
            value_poses += [value_bbox.pos for value_bbox in key_value.value_boxes]
            debug.draw_polys_with_color(image, value_poses, debug.COLOR_GREEN)

            value_text = "".join([value_bbox.txt for value_bbox in key_value.value_boxes])
            logger.info("{:10}\t => {:15s}\t [ 原始文本 \"{}\" =匹配了=> \"{}\" ] ".format(
                        key_value.key_bbox.field['key'].strip(),
                        value_text,
                        key_value.key_bbox.txt,
                        key_value.key_bbox.field['text']))

        cv2.imwrite("debug/" + image_names[i], image)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,handlers=[logging.StreamHandler()])
    process()
