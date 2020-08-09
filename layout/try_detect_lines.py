import os
import sys
import table
import data_loader
from debug import *
from row_parser import *


# 去探测他的value：
# 左面的框的右侧2点的y1,y2，右面的框的左侧2点的y1,y2
def detect_value(bboxes, key_bbox):  # key_bbox[4,2]

    # 按照x的顺序，对bbox进行排序，这个只能用lexsort实现
    # sort_indexs = np.lexsort(key_bbox.T[:1,:])
    # sorted_key_bboxes_by_x = key_bbox[sort_indexs,:] # 从小到大按照x排序
    # key_bbox_right_2_points = sorted_key_bboxes_by_x[2:] # key bboxes右侧2点

    logger.debug("!!!开始分析Key[%r]", key_bbox)
    poses = bbox.get_poses(bboxes)

    # 过滤出任何一个点在 key_bbox的向右的辐射范围内，即目标bbox的任意一个点的y在key_bbox的最大y最小y的"上下"之间
    key_pos = key_bbox.pos
    max_y = np.max(key_pos[:, 1])
    min_y = np.min(key_pos[:, 1])
    larger_indexes = (poses[:, :, 1] > min_y).any(axis=1)
    less_indexes = (poses[:, :, 1] < max_y).any(axis=1)
    poses_left = poses[larger_indexes & less_indexes]
    logger.debug("此Key[%r]同行过滤后，剩余框(%d个)[%r]", key_bbox, len(poses_left),
                 bbox.filter_bboxes_by_poses(bboxes, poses_left))

    # 再继续过滤，所有的备选框，都应该在key的右侧
    key_x = np.min(key_pos[:, 0])
    right_indexes = (poses_left[:, :, 0] > key_x).any(axis=1)
    poses_left = poses_left[right_indexes]
    logger.debug("此Key[%r]再过滤掉左面的，剩余框(%d个)[%r]", key_bbox, len(poses_left),
                 bbox.filter_bboxes_by_poses(bboxes, poses_left))

    # [N,4,2], 按照最左面的x坐标排序
    poses_left = sorted(poses_left, key=lambda x: x[:, 0].min())

    target_value_bboxes = []
    for pos in poses_left:
        _bbox = bbox.find_bbox_by_pos(bboxes, pos)
        if _bbox is None:
            logger.debug("无法通过pos[%r]找到对应bbox", pos)
            continue
        logger.debug("!尝试分析此bbox[%r]....", _bbox)
        if _bbox == key_bbox:
            logger.debug("此框是我自己啊")
            continue  # 排除自己
        ratio = _bbox.vertical_overlay_ratio(key_bbox)
        if ratio < 0.5:
            logger.debug("此框[%r]和key_bbox相交比不达标[%f]，忽略", _bbox, ratio)
            continue
        if _bbox.is_keybbox():  # 如果遇到了下一个key_bbox，那么就结束了
            logger.debug("遇到下一个key[%r]，value截止", _bbox)
            break

        logger.debug("找到value（挨着我的第一个）：%r,距离我：%d", _bbox, key_bbox.horizontal_distance(_bbox))
        target_value_bboxes.append(_bbox)
    return target_value_bboxes


def _merge(_bbox, one_row_bboxes):
    for _check_bbox in one_row_bboxes:
        if _bbox == _check_bbox: continue
        new_bbox = _bbox.merge(_check_bbox)
        if new_bbox is None: continue
        return _check_bbox, new_bbox
    return None, None


# 处理一张图
def process(image, image_name, bboxes):
    logger.debug("开始处理此图的bboxes们：%d个", len(bboxes))

    for _bbox in bboxes:
        cv2.polylines(image, [_bbox.pos], True, COLOR_BLACK, thickness=1)

    exclued_bboxes = exclude_empty_text_bboxes(bboxes)

    good_bboxes, bad_bboxes, average_bbox_height, image_width, image_height = exclude_boxes_by_statistics(bboxes,
                                                                                                          sigma_num=2)

    exclued_bboxes += bad_bboxes

    all_rows, all_row_bboxes = recognize_rough_row(good_bboxes, image_height)

    # 合并一些小框，原则是相距很近，
    # 左右合并
    # 我们的两边相交，或者非常近，有个阈值（比如5个像素内）
    # 而我们y的相交IOU大于0.9，或者其中一个包含另外一个
    # 那么问题来了，如何找到备选的框：好吧，我就遍历每个人，找到candidate
    for i in range(len(all_row_bboxes)):
        one_row_bboxes = all_row_bboxes[i]
        original_size = len(one_row_bboxes)
        logger.debug("旧行[%r]", one_row_bboxes)
        new_one_row_bboxes = []
        while len(one_row_bboxes) > 1:
            need_merged_bbox = one_row_bboxes[0]
            _matched_bbox, new_bbox = _merge(need_merged_bbox, one_row_bboxes[1:])
            if new_bbox is None:
                new_one_row_bboxes.append(need_merged_bbox)
                one_row_bboxes.remove(need_merged_bbox)
            else:
                one_row_bboxes.remove(need_merged_bbox)
                one_row_bboxes.remove(_matched_bbox)
                new_one_row_bboxes.append(new_bbox)
        # 处理最后剩下的1个
        if len(one_row_bboxes) == 1:
            new_one_row_bboxes.append(one_row_bboxes[0])

        # 替换旧有的这行框
        logger.debug("旧行(%d=>%d)合并成[%r]", original_size, len(new_one_row_bboxes), new_one_row_bboxes)
        all_row_bboxes[i] = new_one_row_bboxes

    all_row_bboxes = split_high_rows_2(all_rows, all_row_bboxes, average_bbox_height, image_width)

    image = debug(image, all_rows, all_row_bboxes, exclued_bboxes, image_width)

    name, ext = os.path.splitext(image_name)
    cv2.imwrite("debug/{}_rows.jpg".format(name), image)

    # 按照行的最左面的框的起始Y坐标排序
    logger.debug("按照行的最左面的框的起始Y坐标排序")
    all_row_bboxes = sorted(all_row_bboxes, key=lambda row_bboxes: row_bboxes[0].pos[:, 1].min())
    for row_bboxes in all_row_bboxes:
        logger.debug("行(%d)：%r", len(row_bboxes), row_bboxes)
        if len(row_bboxes) == 1 and len(row_bboxes[0].txt) == 1:
            all_row_bboxes.remove(row_bboxes)
            logger.debug("行%r只有一个字，干扰数据，删除", row_bboxes)
    logger.debug("最终切分出%d行all_rows和%d行all_row_bboxes", len(all_rows), len(all_row_bboxes))

    extract_key_values2(all_row_bboxes, image, "key-value")

    extract_tables(all_row_bboxes, average_bbox_height, image_height, image_width)

    extract_key_values2(all_row_bboxes, image, key_type="key-value,table")

    image = debug(image, all_rows, all_row_bboxes, exclued_bboxes, image_width)
    cv2.imwrite("debug/{}".format(image_name), image)

    return image


def extract_tables(all_row_bboxes, average_bbox_height, image_height, image_width):
    # 对行按照第一个元素的Y进行排序
    all_row_bboxes = sorted(all_row_bboxes, key=lambda row_bboxes: row_bboxes[0].pos[:, 1].min())
    # 遍历每一行
    for i in range(len(all_row_bboxes)):
        bboxes_of_row = all_row_bboxes[i]
        # 找出这一行的所有的bboxes
        key_counter = 0
        for _bbox in bboxes_of_row:
            field = bbox.find_similar_key(_bbox.txt, "table")
            if not field:
                field = bbox.find_similar_key(_bbox.txt, "key_value,table")
            if field:
                logger.debug("此bbox[%s]匹配文本为[%s]的key[%s]", _bbox.txt, field['text'], field['key'])
                _bbox.field = field  # <------- 把field，类似于meta放置入bbox肚子里
                key_counter += 1
        # 计算这行的bbox们，多少比例是key标题
        title_key_ratio = key_counter / len(bboxes_of_row)

        if title_key_ratio >= 0.5 and len(bboxes_of_row) >= 3:
            logger.debug("这行有[%d]个标题，超过3个，60%%的标题都是key，我有理由相信他是表格标题行:", len(bboxes_of_row))

            # 只build从表格标题行往后的行：all_row_bboxes[i + 1:]
            __table = table.table_builder(bboxes_of_row, all_row_bboxes[i + 1:], average_bbox_height, image_width,
                                          image_height)

            # # 先把header bboxes从大池子里删掉
            # for __row in __table.rows:
            #     for __col in __row.columns:
            #         for __bbox in __col.bboxes:
            #             if __bbox in __bbox: good_bboxes.remove(__bbox)
            # for __header_column in __table.header_columns:
            #     if __header_column.header_bbox in good_bboxes:
            #         good_bboxes.remove(__header_column.header_bbox)

            logger.info("\n\n表格：")
            logger.info(
                "=============================================================================================================================")
            logger.info("\t|\t".join([str(header_bbox) for header_bbox in bboxes_of_row]))
            logger.info(str(__table))
            logger.info(
                "=============================================================================================================================")
            logger.info("\n\n")
        else:
            logger.debug("此行[%d]个框,[%d]是潜在表标题,比例[%.2f]", len(bboxes_of_row), key_counter, title_key_ratio)


def extract_key_values(good_bboxes, image, key_type):
    # 找出所有的强key-value，所谓"强"，就是他肯定不会出现在table中的bboxes
    key_values = []  # 所有的key：value对，1：N的关系，可能有多个value bboxes
    for _bbox in good_bboxes:
        text = _bbox.txt
        field = bbox.find_similar_key(text, key_type)
        if field:
            logger.debug("此bbox[%s]匹配文本为[%s]的key[%s]", text, field['text'], field['key'])
            _bbox.field = field  # <------- 把field，类似于meta放置入bbox肚子里
            key_values.append(bbox.KeyValue(_bbox, field))
    # 先把key都从旧集合中删除掉
    for key_value in key_values:
        good_bboxes.remove(key_value.key_bbox)
    # 为每个key去找value
    for key_value in key_values:
        key_bbox = key_value.key_bbox
        logger.debug("处理其中的一个key：%s", key_bbox.txt)

        value_bboxes = detect_value(good_bboxes, key_bbox)
        if len(value_bboxes) == 0:
            logger.debug("无法为它找到value")
            continue

        logger.debug("!!!找到Key：%s ==> Value: %r", key_bbox.txt, value_bboxes)

        key_value.value_bboxes += value_bboxes
        for vb in value_bboxes:
            good_bboxes.remove(vb)  # 把这个value_bbox从原始的bboxes集合中都删除掉

    # 打印key value信息
    for key_value in key_values:
        key_pos = key_value.key_bbox.pos
        draw_poly_with_color(image, key_pos, COLOR_RED)

        value_poses = []
        value_poses += [value_bbox.pos for value_bbox in key_value.value_bboxes]
        draw_polys_with_color(image, value_poses, COLOR_GREEN)

        value_text = "".join([value_bbox.txt for value_bbox in key_value.value_bboxes])
        logger.info("{:10}\t => {:15s}\t [ 原始文本 \"{}\" =匹配了=> \"{}\" ] ".format(
            key_value.key_bbox.field['key'].strip(),
            value_text,
            key_value.key_bbox.txt,
            key_value.key_bbox.field['text']))


import parse_key_values


def extract_key_values2(all_row_bboxes, image, key_type):
    # 用来存放这样行的所有的key-values
    all_key_values = []
    for one_row_bboxes in all_row_bboxes:
        logger.debug("Key分析：开始分析这一行：%r", one_row_bboxes)
        one_row_key_values = []
        for _bbox in one_row_bboxes:

            logger.debug("开始处理bbox：%r", _bbox)
            # 返回这个bbox对应的key-value对，最后还有个上一个key对应的value
            key_values, previous_value_bbox = parse_key_values.process_bbox(_bbox, key_type)

            if previous_value_bbox and len(one_row_key_values) == 0:
                logger.debug("不对啊，为这个value[%s]找不到前面的key啊", previous_value_bbox.txt)
            if previous_value_bbox and len(one_row_key_values) > 0:
                previous_key_value = one_row_key_values[-1]
                logger.debug("当前bbox[%r]包含上一个key[%r]的value[%r]", _bbox, previous_key_value, previous_value_bbox)
                previous_key_value.append_value_box(previous_value_bbox)

            if not key_values: continue

            one_row_key_values += key_values

        if len(one_row_key_values) > 0:
            logger.debug("这行原始bboxes包含%d个key-value", len(one_row_key_values))
            all_key_values.append(one_row_key_values)
            all_row_bboxes.remove(one_row_bboxes)
        else:
            logger.debug("这行原始bboxes不包含任何key-value:%r", one_row_bboxes)

    # 打印key value信息
    for row_key_values in all_key_values:
        for key_value in row_key_values:
            key_pos = key_value.key_bbox.pos
            draw_poly_with_color(image, key_pos, COLOR_RED)

            value_poses = []
            logger.debug("Key-Value:%r", key_value)
            value_poses += [value_bbox.pos for value_bbox in key_value.value_bboxes]
            draw_polys_with_color(image, value_poses, COLOR_GREEN)

            value_text = "".join([value_bbox.txt for value_bbox in key_value.value_bboxes])
            # print(key_value)
            # print(key_value.key_bbox)
            # print(key_value.key_bbox.field)
            logger.info("{:10}\t => {:15s}\t [ 原始文本 \"{}\" =匹配了=> \"{}\" ] ".format(
                key_value.field['key'].strip(),
                value_text,
                key_value.key_bbox.txt,
                key_value.field['text']))


# TODO：矩形识别旋转的算法大bug

if __name__ == '__main__':

    debug_level = logging.DEBUG
    if len(sys.argv) == 2:
        if sys.argv[1] == "info":
            debug_level = logging.INFO
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=debug_level,
                        handlers=[logging.StreamHandler()])

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
        logger.info("    %s", image_names[i])
        logger.info("========================================================")
        image = process(images[i], image_names[i], one_image_bboxes)
