import math, numpy as np, cv2, logging
from shapely.geometry import *

logger = logging.getLogger(__name__)


# 找到矩形的中心点（可能矩形是倾斜的）,[4,2]
def caculate_rect_center(rect):
    rect = np.array(rect)
    x_left = rect[:, 0].min()
    x_right = rect[:, 0].max()
    y_top = rect[:, 1].min()
    y_buttom = rect[:, 1].max()
    x = x_left + (x_right - x_left) / 2
    y = y_top + (y_buttom - y_top) / 2
    logger.debug("矩形中心：%r", [x, y])
    return [x, y]


# 对矩形的4个点按照顺时针顺序排序，从最上面的点开始
def sort_rect_points(rect):
    top_index = rect[:, 1].argmin()  # 最上面的点
    top_point = rect[top_index]
    bottom_index = rect[:, 1].argmax()  # 最下面的点
    bottom_point = rect[bottom_index]
    left_index = rect[:, 0].argmin()  # 最左的点
    left_point = rect[left_index]
    right_index = rect[:, 0].argmax()  # 最右面的点
    right_point = rect[right_index]
    return np.array([top_point, right_point, bottom_point, left_point])


# 计算一个矩形的倾斜角，是按照水平+顺时针计算的，
# 例如：结果为30度，意味着这个三角形从水平方向，顺时针转了30度
def caculate_rect_inclination(rect):
    line1, _ = find_longer_2_lines_of_bbox(rect)
    if line1 is None:
        return math.radians(90)
    k = line1[2]
    arc = math.atan(k)
    if math.isnan(arc):
        arc = math.radians(90)
    degree = math.degrees(arc)
    logger.debug("矩形倾斜角度为：%r度，弧度值为：%f", degree, arc)
    return arc


def test1():
    polygon = [[40, 20], [150, 50], [240, 130], [80, 120]]
    shapely_poly = Polygon(polygon)

    line = [(10, 20), (220, 180)]
    shapely_line = LineString(line)

    # intersection_line = list(shapely_poly.intersection(shapely_line).coords)
    # print(intersection_line.area)

    splited1,splited2 = split(shapely_poly,shapely_line)
    area1 = splited1.area
    area2 = splited2.area


    if area1>area2:
        big_split_polygon = splited1.exterior.coords
    else:
        big_split_polygon = splited2.exterior.coords
    # print(list(big_split_polygon))
    big_split_polygon = np.array(list(big_split_polygon),np.int32)

# line1，line2是一个组平行线，line形如[p1,p2,k]，像一个手电筒射出的平行光柱
# 这个函数用来计算，目标bbox被这个光柱找到的面积比，也即是被平行线切除的面积 / 他自己的面积
def spotlight_intersection_ratio(current_bbox, line1, line2, bbox, image_width=10000):

    # 1. 计算line1上的右侧点
    # 选择一个适度的右方探测x
    p1, p2, k1 = line1
    # 右侧选择一个点，用于形成一个四边形
    detect_x = p1[0] + image_width * 0.5 # TODO 这个参数之前调整到0.75，效果更好，但是0.75会导致4变形交叉
    # 计算第一条直线的截距b
    b1 = p1[1] - k1 * p1[0]  # y=kx+b => b=y-kx
    # 得到右侧的x在这条直线上的点 p_end1
    p_end1 = [detect_x, k1 * detect_x + b1]

    # 2. 计算line2上的右侧点
    p3, p4, k2 = line2
    b2 = p3[1] - k2 * p3[0]  # y=kx+b => b=y-kx
    p_end2 = [detect_x, k2 * detect_x + b2]

    # 围成一个四边形
    if p1[0] <p2[0]:
        left1 = p1
    else:
        left1= p2
    if p3[0] <p4[0]:
        left2 = p3
    else:
        left2= p4
    spotlight_poly = [left1, p_end1, p_end2, left2]

    # print(spotlight_poly)
    # print("bbox.pos")
    # print(bbox.pos)
    spotlight_poly = Polygon(spotlight_poly)
    poly = Polygon(bbox.pos)
    # print("---------")
    # print([p1, p_end1, p_end2, p3])
    # print(bbox.pos)
    intersection_area = spotlight_poly.intersection(poly).area
    bbox_area = poly.area

    ratio = intersection_area / bbox_area
    # logger.debug("intersection_area:%f", intersection_area)
    # logger.debug("bbox_area:%f", bbox_area)
    logger.debug("行识别：辐射bbox[%r][%f]辐射目标bbox[%r][%f]，辐射面积占比[%.2f]", current_bbox,intersection_area, bbox,bbox_area, ratio)
    return ratio


# 找到bbox的两条接近水平的两条线
def find_approximate_horizontal_2_lines_of_bbox(bbox):
    pos = bbox.pos
    # logger.info("pos[%r],text[%s]",pos,bbox.txt)
    assert pos.shape == (4, 2), str(pos)
    points_num = len(pos)  # 虽然可以直接写4，还是尽量灵活一些，万一未来要改成多边形呢

    horizontal_lines = []
    for i in range(points_num):
        p1 = pos[i]
        p2 = pos[(i + 1) % points_num]

        # 计算两两之间的线段的斜率
        if (p1[0] - p2[0]) == 0:
            logger.debug("行识别：此框的点[%r,%r]形成的为竖直的", p1, p2)
            k = 100000  # 随便是个大数
        else:
            k = (p1[1] - p2[1]) / (p1[0] - p2[0])
        if abs(k) <= 1:
            logger.debug("行识别：此框的点[%r,%r]形成的|斜率|<1(45度以内)：%.2f", p1.tolist(), p2.tolist(), k)
            horizontal_lines.append([p1, p2, k])

    logger.debug("行识别：为bbox[%r]找到[%d]条接近水平的边", bbox, len(horizontal_lines))
    return horizontal_lines


# 找到bbox的两条长边的直线方程，bbox一定是个矩形，但是可能是倾斜的
def find_longer_2_lines_of_bbox(pos):
    # pos = bbox.pos
    # assert pos.shape == (4, 2), str(pos)
    points_num = len(pos)  # 虽然可以直接写4，还是尽量灵活一些，万一未来要改成多边形呢

    # 先按照最高点，然后顺时针对点进行排序
    # pos = sort_pos_points(pos)

    # 计算矩形各边长度
    length = []
    for i in range(points_num):
        length.append(np.linalg.norm(pos[i] - pos[(i + 1) % points_num]))

    # 找到最长的边
    max_index = length.index(max(length))

    # 找到最长的边对应的2个点
    p1 = pos[max_index]
    p2 = pos[(max_index + 1) % points_num]
    # print("p1,p2:",p1,"/",p2)
    # print(bbox.txt.strip()=="")
    # print("bbox:[%r]" % len(bbox.txt))
    if (p1[0] - p2[0]) == 0:
        logger.debug("行识别：此框[%r]长边为竖直的")
        return None,None
    k1 = (p1[1] - p2[1]) / (p1[0] - p2[0])

    # 找到另外一条长边的2个点
    p3 = pos[(max_index + 2) % points_num]
    p4 = pos[(max_index + 3) % points_num]
    (p3[0] - p4[0])
    k2 = (p3[1] - p4[1]) / (p3[0] - p4[0])

    logger.debug("行识别：为bbox[%r]找到两条长边[k1/k2][%.2f,%.2f]", pos, k1, k2)
    return [p1, p2, k1], [p3, p4, k2]


# 按照矩形中心点，顺时针旋转a（弧度）：rect[4,2], center[2]
def rotate_rect_by_center(rect, radian):
    """
    a表示矩形的旋转角度，为弧度。
    rect为矩形4点坐标
    返回：旋转后的4点坐标
    """
    # 选中中心
    _center = caculate_rect_center(rect)

    cx = _center[0]
    cy = _center[1]
    rotated_rect = []

    for p in rect:
        x = p[0]
        y = p[1]
        # 以[cx,cy]为中心点逆时针旋转
        x0 = (x - cx) * math.cos(radian) - (y - cy) * math.sin(radian) + cx
        y0 = (x - cx) * math.sin(radian) + (y - cy) * math.cos(radian) + cy
        rotated_rect.append([x0, y0])
    logger.debug("矩形按照中心点[%r]顺时针旋转了[%f]度", _center, math.degrees(radian))
    logger.debug("[%r]=>[%r]", rect, rotated_rect)
    return np.array(rotated_rect, np.int32)


def rotate_rect_to_horizontal(rect):
    rotated_arc = caculate_rect_inclination(rect)
    if rotated_arc == 0:
        logger.debug("矩形倾斜角度为0，无需旋转")
        return rect
    return rotate_rect_by_center(rect, -rotated_arc)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    image = np.full([400, 400, 3], 255, np.uint8)
    rect = np.array([[50, 50], [150, 50], [150, 100], [50, 100]])
    cv2.polylines(image, [rect], isClosed=True, color=(255, 0, 0), thickness=2)
    rect = rotate_rect_by_center(rect, radian=math.radians(30))
    logger.debug("旋转30度后的坐标为：%r", rect)
    rotated_arc = caculate_rect_inclination(rect)
    cv2.polylines(image, [rect], isClosed=True, color=(0, 0, 255), thickness=2)

    # 把倾斜30度的矩形框，摆平 红色=>绿色
    rect = np.array([[72, 128],
                     [155, 178],
                     [130, 221],
                     [34, 171]])
    cv2.polylines(image, [rect], isClosed=True, color=(0, 0, 255), thickness=2)
    rect = rotate_rect_to_horizontal(rect)
    cv2.polylines(image, [rect], isClosed=True, color=(0, 255, 0), thickness=2)

    cv2.imwrite("debug/test.jpg", image)
