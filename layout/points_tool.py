import math, numpy as np, cv2, logging

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
def caculate_rect_inclination(rect,image=None):
    assert rect.shape == (4, 2), str(rect)
    points_num = len(rect)  # 虽然可以直接写4，还是尽量灵活一些，万一未来要改成多边形呢

    # 先按照最高点，然后顺时针对点进行排序
    # rect = sort_rect_points(rect)

    # 计算矩形各边长度
    length = []
    for i in range(points_num):
        length.append(np.linalg.norm(rect[i] - rect[(i+1) % points_num]))

    # print(length)
    max_index = length.index(max(length))
    # print(max_index)
    p1 = rect[max_index]
    p2 = rect[(max_index + 1) % points_num]

    logger.debug("找到矩形最长的边：%r=>%r", p1.tolist(), p2.tolist())
    if image is not None:
        cv2.line(image,tuple(p1.tolist()),tuple(p2.tolist()),color=(0,0,255),thickness=3)
    k = (p1[1] - p2[1]) / (p1[0] - p2[0])

    arc = math.atan(k)
    if math.isnan(arc):
        arc = math.radians(90)
    degree = math.degrees(arc)
    logger.debug("矩形倾斜角度为：%r度，弧度值为：%f", degree, arc)

    return arc


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


def rotate_rect_to_horizontal(rect, image=None):
    rotated_arc = caculate_rect_inclination(rect,image)
    if rotated_arc == 0:
        logger.debug("矩形倾斜角度为0，无需旋转")
        return rect
    return rotate_rect_by_center(rect,-rotated_arc)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    image = np.full([400, 400, 3], 255, np.uint8)
    rect = np.array([[50, 50],[150, 50],[150, 100],[50, 100]])
    cv2.polylines(image, [rect], isClosed=True, color=(255, 0, 0), thickness=2)
    rect = rotate_rect_by_center(rect, radian=math.radians(30))
    logger.debug("旋转30度后的坐标为：%r",rect)
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
