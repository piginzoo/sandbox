#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import logging
import bbox
import points_tool

logger = logging.getLogger(__name__)


# 找出一行的bboxes拟和的线段的中点的y值
def get_bboxes_fit_line_middle_y(row_bboxes):
    X=[], Y=[]
    for bbox in row_bboxes:
        X.append((bbox.pos[:, 0].max - bbox.pos[:0].min) / 2)
        Y.append((bbox.pos[:, 1].max - bbox.pos[:1].min) / 2)
    line = np.polyfit(X, Y, 1)
    line = np.poly1d(line)
    y = line(max(X) - min(X))
    return y

def calculate_2_row_bboxes_distance(row_bboxes1,row_bboxes2):
    y1 = get_bboxes_fit_line_middle_y(row_bboxes1)
    y2 = get_bboxes_fit_line_middle_y(row_bboxes2)
    return y2 - y1

def split_high_rows_2(all_rows, all_rows_bboxes, row_avarage_height, image_width):
    new_all_rows_bboxes = []

    LINE_RATIO = 1

    for i in range(all_rows.shape[0]):
        row = all_rows[i]
        one_row_bboxes = all_rows_bboxes[i]

        # 得到这行的行高
        row_height = abs(row[1] - row[0])

        # 如果这行在标准差的 LINE_RATIO 倍以内，就认为是正常行，不处理
        if row_height < LINE_RATIO * row_avarage_height:
            new_all_rows_bboxes.append(one_row_bboxes)
            logger.debug("此行高[%f]在%f倍均高[%f]内，属于正常行", row_height, LINE_RATIO, LINE_RATIO * row_avarage_height)
            continue

        logger.debug("此行为超高行，好吧，我们来肢解他，他一共[%d]个bbox", len(one_row_bboxes))

        new_small_row_counter = 0
        while len(one_row_bboxes) != 0:
            # 按左上角排序,从小到大
            logger.debug("行识别：先对备选bboxes们[%d]个，按照x坐标标排序", len(one_row_bboxes))
            one_row_bboxes = sorted(one_row_bboxes, key=lambda _bbox: _bbox.pos[:, 0].min())

            # 把当前的bbox加入到新行
            new_small_row_counter += 1
            new_row_bboxes = []
            current_detect_bbox = one_row_bboxes[0]
            one_row_bboxes.remove(current_detect_bbox)  # 一删
            new_row_bboxes.append(current_detect_bbox)  # 一加

            logger.debug("行识别：创建新行，并且把当前框[%r]加入新行", current_detect_bbox)

            while current_detect_bbox:
                found_next_bbox = find_spotlight_target(current_detect_bbox, candiate_bboxes=one_row_bboxes,
                                                        image_width=image_width)
                if found_next_bbox:
                    if len(found_next_bbox.txt.strip()) == 1:  # 如果新找到的是一个单字，不考虑用他当最新的探测狂，继续使用旧的
                        logger.debug("行识别：找到一个辐射满足框，但是个单字框[%r]，继续使用上一个bbox[%r]作为探测框", found_next_bbox,
                                     current_detect_bbox)
                        one_row_bboxes.remove(found_next_bbox)  # 一删
                        continue
                    current_detect_bbox = found_next_bbox
                    one_row_bboxes.remove(current_detect_bbox)  # 一删
                    new_row_bboxes.append(current_detect_bbox)  # 一加
                    logger.debug("行识别：找到一个辐射满足框[%r]，加入当前行，用它来继续探测", found_next_bbox)
                else:
                    logger.debug("行识别：用当前bbox[%r]来找下一个失败了，此行已经到头了", current_detect_bbox)
                    break
            new_all_rows_bboxes.append(new_row_bboxes)
            logger.debug("行识别：! 完成新行的探测，捕获了[%d]个bbox，剩余[%d]没娘的孩子", len(new_row_bboxes), len(one_row_bboxes))
        logger.debug("行识别：!! 此大行一共肢解成[%d]个新小行", new_small_row_counter)
    return new_all_rows_bboxes


# 尝试从备选集合中，找到第一个候选的右侧可以串成行的bbox
def find_spotlight_target(current_bbox, candiate_bboxes, image_width):
    # 先按x排序
    sorted_candiate_bboxes = sorted(candiate_bboxes, key=lambda _bbox: _bbox.pos[:, 0].min())

    for next_bbox in sorted_candiate_bboxes:

        if not current_bbox.left_of(next_bbox) and current_bbox.is_overlap(next_bbox):
            logger.debug("行识别：备选bbox[%r]不在当前bbox[%r]的右面，且不相交，怒略", next_bbox, current_bbox)
            continue

        # 找到当前框的长边的2条线
        line1, line2 = points_tool.find_approximate_horizontal_2_lines_of_bbox(current_bbox)
        # 计算下一个
        ratio = points_tool.spotlight_intersection_ratio(current_bbox, line1, line2, next_bbox, image_width)
        if ratio > 0.5:
            logger.debug("行识别：找到和当前bbox[%r]的下一个bbox[%r]，接力棒给他", current_bbox, next_bbox)
            return next_bbox
        else:
            # 如果不满足，这个框先丢掉，等待下一轮测试
            logger.debug("行识别：这个bbox[%r]的辐射相交率[%r]不满足0.5，拿走等待下轮尝试", next_bbox, ratio)

    logger.debug("行识别：没有为[%r]找到任何可以手电筒照射到靠谱的备选bbox，好失望", current_bbox)
    return None


# 把一个过高的行分割成多行
def split_high_rows(rows, row_elements, row_avarage_height):
    logger.debug("一共%d行，行均高mean+1std:%f" % (len(rows), row_avarage_height))

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

        # 如果这行在标准差的 LINE_RATIO 倍以内，就认为是正常行，不处理
        if row_height < LINE_RATIO * row_avarage_height:
            new_rows.append(row)
            new_rows_elements.append(row_elements[i])
            logger.debug("此行高[%f]在%f倍均高[%f]内，属于正常行", row_height, LINE_RATIO, LINE_RATIO * row_avarage_height)
            continue

        logger.debug("此行高[%f]超预定义行高[%f]，需要分拆..." % (row_height, LINE_RATIO * row_avarage_height))

        polys = row_elements[i]
        logger.debug("此行目前包含一共[%d]个bbox", len(polys))

        # 按左上角排序,从小到大，返回的是一个list，不是numpy？
        sorted_polys = sorted(polys, key=lambda x: x[:, 1].min())

        logger.debug("先对行内小框们按照左上角坐标排序")

        # 定义一个新行的【高度】（注意不是新行起始y） ，行高还是规定的行的高度
        new_row_height = LINE_RATIO * row_avarage_height  # <------------------------------------------------ 这个是最关键的，确定行高
        logger.debug("定义新行高[%f]", new_row_height)

        left_polys_of_row = sorted_polys
        while (len(left_polys_of_row) != 0):

            # 得到新行的【起始位置】，就是最靠上poly(也就是第一个)的左上角坐标,[4,2]
            new_row_y1 = left_polys_of_row[0][:, 1].min()  # 4点里的最小y值
            new_row_y2 = new_row_y1 + new_row_height
            logger.debug("确定新行的y1:%d,y2:%d" % (new_row_y1, new_row_y2))

            # 然后用新的y1,y2去过滤小框们，形成一个新行，直到处理完毕
            new_poloys_of_row = []
            exclude_poloys_of_row = []

            # 遍历剩下的bbox，看看他的最下面(最大的y)是否在新行内，如果在，加入到新行
            for poly in left_polys_of_row:
                p_y1 = poly[:, 1].min()
                p_y2 = poly[:, 1].max()

                if p_y1 >= new_row_y1 and new_row_y2 >= p_y2:
                    logger.debug("此bbox框完全被新行包裹，加入新行集合")
                    new_poloys_of_row.append(poly)
                    continue

                y_height1 = abs(p_y1 - new_row_y2)
                y_height2 = abs(p_y2 - new_row_y1)
                y_height_ratio = min(y_height1, y_height2) / max(y_height1, y_height2)
                if y_height_ratio > 0.5:
                    logger.debug("此bbox框的一半在新行的内，加入新行集合")
                    new_poloys_of_row.append(poly)
                    continue

                logger.debug("此bbox框相交不足行0.5[%f]，无法归入新行: 框高[%f]，行高[%f]",
                             y_height_ratio,
                             abs(p_y1 - p_y2),
                             abs(new_row_y2 - new_row_y1))
                exclude_poloys_of_row.append(poly)

            new_row = [new_row_y1, new_row_y2]
            new_rows.append(new_row)
            new_rows_elements.append(new_poloys_of_row)
            logger.debug("%d个小框加入新行%r" % (len(new_poloys_of_row), new_row))

            # 剔除已经归队的小框门，继续这个过程，直到为空
            left_polys_of_row = exclude_poloys_of_row
            logger.debug("排序的原有行的小框数量剩余：%d,剔除: %d" % (len(left_polys_of_row), len(new_poloys_of_row)))

    return new_rows, new_rows_elements


def exclude_empty_text_bboxes(bboxes):
    exclued_bboxes = []
    left_bboxes = []
    original_size = len(bboxes)
    for _bbox in bboxes:
        if _bbox.txt.strip() == "":
            logger.debug("此框识别文字为空，怒弃")
            exclued_bboxes.append(_bbox)
            bboxes.remove(_bbox)
        else:
            left_bboxes.append(_bbox)
    logger.debug("原bboxes[%d]个，删除了[%d]个空字符串的，还剩[%d]个",
                 original_size,
                 len(exclued_bboxes),
                 len(left_bboxes))
    return left_bboxes, exclued_bboxes


def exclude_boxes_by_statistics(bboxes, sigma_num=2):
    poses = bbox.get_poses(bboxes)
    good_poses, mean, bad_poses = exclude_1sigma(poses, sigma_num=sigma_num)
    height = good_poses[:, :, 1].max()  # 所有bbox的最大的y
    width = good_poses[:, :, 0].max()  # 所有bbox的最大的x
    logger.debug("图像宽[%d],高[%d]", width, height)
    good_bboxes = bbox.filter_bboxes_by_poses(bboxes, good_poses)
    bad_bboxes = bbox.filter_bboxes_by_poses(bboxes, bad_poses)
    logger.debug("原bboxes[%d]个，删除了[%d]个2sigma外的，还剩[%d]个",
                 len(bboxes), len(bad_poses), len(good_poses))
    return good_bboxes, bad_bboxes, mean, width, height


# 剔除一个标准差之外的数据
# poses,原始数据[N,4,2] : [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
def exclude_1sigma(poses, sigma_num=2):
    # 把[N,4,2]变成[N],里面放着每个框的高度
    data = np.array(poses)
    data = np.array(data[:, :8], np.float)
    data = data.reshape(-1, 4, 2)
    heights = data[:, :, 1].max(axis=1) - data[:, :, 1].min(axis=1)

    std = heights.std()
    max = heights.max()
    min = heights.min()
    mean = heights.mean()
    logger.debug("数据情况：mean={},std={},max={},min={}".format(mean, std, max, min))

    max_height = mean + sigma_num * std
    min_height = mean - sigma_num * std
    logger.debug("%d个标准差下，最大高度为：%f，最小高度为：%f", sigma_num, max_height, min_height)

    bad_heights_indices = np.where(np.logical_or(heights > 2 * mean, \
                                                 heights < min_height, \
                                                 heights > max_height))
    bad = [poses[i] for i in bad_heights_indices[0]]

    # TODO ??? 不知道为何"heights <= 2*mean"条件放最后，就无法起到过滤作用？！
    good_heights_indices = np.where(np.logical_and(heights <= 2 * mean,
                                                   heights <= max_height, \
                                                   heights >= min_height))
    good = [poses[i] for i in good_heights_indices[0]]

    logger.debug("一共有%d个框，正常框[%d]个，异常框框[%d]", len(heights), len(good), len(bad))
    return np.array(good), mean, np.array(bad)


# 输入：是图片高度，和小框们
# 输出：每一个行的起始和终止Y值，如：[[0,15],[28,35],...]
# 这个方法，只是看投影，只要有投影，就说明还是在一个大的行内，所以，他的问题是，可能会切割出很高的行
# 高行会在后面处理
def recognize_rough_row(bboxes, image_height):
    logger.debug("进行行识别，数据:%r，图像高度：%d", len(bboxes), image_height)
    h_array = np.zeros(image_height, dtype=np.int32)

    # 先都往y轴上做投影
    for bbox in bboxes:  # 一个框
        pos = bbox.pos
        pos = pos[:8]  # 去除文本
        pos = np.array(pos, np.float).astype(np.int32)
        pos = pos.reshape(4, 2)
        y1 = pos[:, 1].min()
        y2 = pos[:, 1].max()
        # 向Y轴做投影
        h_array[y1:y2] = 1

    pre_value = 0
    rows = []

    # 从0跃迁到1的连续区间，记录其开始、结束为止，即投影线段，h_array是一个图像高为长度的一个0/1数组
    for i, value in enumerate(h_array.tolist()):
        if pre_value == 0 and value == 1:
            rows.append(i)
        if pre_value == 1 and value == 0:
            rows.append(i)
        pre_value = value
    logger.debug("先做行投影找到连续行%d个", len(rows))

    # 让最后的点是偶数
    if len(rows) % 2 != 0:
        # logger.debug("行[%d]y1y2需为偶数，增加一行",len(rows))
        rows.append(image_height)

    rows = np.array(rows)
    rows = rows.reshape(-1, 2)

    # 每个框都归队
    row_elements = []
    for row in rows:
        one_row_elements = []

        remove_index = []
        # logger.debug("处理一行：%r",row)
        for bbox in bboxes:  # 一个框

            pos = bbox.pos[:8]
            pos = np.array(pos, np.float).astype(np.int32)
            pos = pos.reshape(4, 2)
            y1 = pos[0, 1]
            y2 = pos[3, 1]

            # 如果这个框的投影在某个行内，就归队到这行，然后在总集合中剔除他
            if y1 >= row[0] and y2 <= row[1]:
                logger.debug("此bbox框[%r]投影在行内：y1[%d]>=row_y1[%d],y2[%d]<=row_y2[%d]:", bbox, y1, y2, row[0], row[1])
                one_row_elements.append(bbox)
                # logger.debug("这个框的投影在行内，归队TA，并在总集合中剔除他:y1(%d)>row_y1(%d),y2(%d)<row_y2(%d)" % (y1,row[0],y2,row[1]))
        row_elements.append(one_row_elements)

    # rows和row_elements行数是一样的，对应行就是对应的框们
    logger.debug("识别出%d行", len(row_elements))
    return rows, row_elements
