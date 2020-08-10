import re
from row_parser import *
import Levenshtein
from fields import *

logger = logging.getLogger(__name__)


class KeyValue():

    def __init__(self, key_bbox, field, parent_bbox=None):  # 可能是一个keybox里面的子keybox
        self.value_bboxes = []
        self.key_bbox = key_bbox
        self.field = field
        if parent_bbox:
            self.parent_bbox = parent_bbox
        else:
            self.parent_bbox = key_bbox

    def append_value_box(self, value):
        if type(value) == list:
            self.value += value
        assert type(value) == BBox
        self.value_bboxes.append(value)

    def __to_string(self):
        value = "".join([bbox.txt for bbox in self.value_bboxes])
        return "{}:{}".format(self.key_bbox, value)

    def __str__(self):
        return self.__to_string()

    def __repr__(self):
        return self.__to_string()

    def __eq__(self, other):
        return self.key_bbox == other.key_bbox


class BBox():
    VERTICAL_MAX_DISTANCE = 5  # 上下相距5像素算很近
    HORIZENTAL_MAX_DISTANCE = 0  # 左右相距0像素才算很近
    MIN_OVERLAP_RATIO = 0.9  # 至少90%交并比才算真正相交

    # 用于创建一个虚拟bbox
    def create_virtual_bbox(text):
        return BBox(np.zeros((4, 2)), text)

    def __init__(self, pos, txt):
        if type(pos) == list: pos = np.array(pos)
        assert pos.shape == (4, 2)
        self.pos = pos
        self.txt = txt
        self.field = None

    def __str__(self):
        return self.txt  # + " " + str(self.pos.tolist())

    def __repr__(self):
        return self.txt  # + " " + str(self.pos.tolist())

    def __hash__(self):
        key = str(self.pos.tolist()) + self.txt
        logger.debug("hash[%r]的key为：%s", self, key)
        return hash(key)

    def __eq__(self, other):
        # 如果自己本身就是个无效坐标（虚拟bbox），就跟谁也不相同
        if (self.pos == 0).all():
            logger.debug("我是一个虚拟bbox")
            return False
        if (self.pos == other.pos).all():
            logger.debug("other[%s]和我[%s]相等", other.txt, self.txt)
            return True
        return False

    def height(self):
        return self.pos[:, 1].max() - self.pos[:, 1].min()

    def width(self):
        return self.pos[:, 0].max() - self.pos[:, 0].min()

    def left(self):
        return self.pos[:, 0].min()

    def right(self):
        return self.pos[:, 0].max()

    def top(self):
        return self.pos[:, 1].min()

    def bottom(self):
        return self.pos[:, 1].max()

    def left_of(self, other):
        my_right = self.pos[:, 0].min()  # 我的最右面
        his_left = other.pos[:, 0].min()  # 你的最左面
        return his_left > my_right

    # TODO：有个开源项目：http://www.angusj.com/delphi/clipper.php ，可以参考并利用
    def is_overlap(self, other):
        self.horizontal_distance(other) == 0 and \
        self.vertical_distance(other) == 0

    def edit_distance(self, text):
        return Levenshtein.distance(text, self.txt)

    # 看左右距离,
    def horizontal_distance(self, other_bbox):
        other_pos = other_bbox.pos
        # x1左，x2右
        my_x1 = self.pos[:, 0].min()
        my_x2 = self.pos[:, 0].max()
        his_x1 = other_pos[:, 0].min()
        his_x2 = other_pos[:, 0].max()
        if my_x2 < his_x1: return his_x1 - my_x2  # 我在左面
        if my_x1 > his_x2: return my_x1 - his_x2  # 我在右面
        return 0  # 我俩相交

    # 看上下距离
    def vertical_distance(self, other):
        # y1上，y2下
        my_y1 = self.pos[:, 1].min()
        my_y2 = self.pos[:, 1].max()
        his_y1 = other.pos[:, 1].min()
        his_y2 = other.pos[:, 1].max()
        if my_y2 < his_y1: return his_y1 - my_y2  # 我在上面
        if my_y1 > his_y2: return my_y1 - his_y2  # 我在下面
        return 0  # 我俩相交

    def merge(self, other):
        # logger.debug("[%s]/[%s]水平重叠度：%f",self.txt,other.txt,self.horizontal_overlay_ratio(other))
        # logger.debug("[%s]/[%s]竖直距离：%f",self.txt,other.txt,self.vertical_distance(other))
        # logger.debug("[%s]/[%s]竖直重叠度：%f",self.txt,other.txt,self.vertical_overlay_ratio(other))
        # logger.debug("[%s]/[%s]水平距离：%f",self.txt,other.txt,self.horizontal_distance(other))
        # 上下合并
        if self.horizontal_overlay_ratio(other) > BBox.MIN_OVERLAP_RATIO and \
                self.vertical_distance(other) <= BBox.VERTICAL_MAX_DISTANCE:
            top = min(self.top(), other.top())
            bottom = max(self.bottom(), other.bottom())
            left = min(self.left(), other.left())
            right = max(self.right(), other.right())
            pos = np.array([[left, top], [right, top], [right, bottom], [left, bottom]])
            if self.top() < other.top():
                text = self.txt + other.txt
            else:
                text = other.txt + self.txt
            logger.debug("我[%r]和[%r]上下合并[%s]", self, other, text)
            return BBox(pos, text)
        # 左右合并
        if self.vertical_overlay_ratio(other) > BBox.MIN_OVERLAP_RATIO and \
                self.horizontal_distance(other) <= BBox.HORIZENTAL_MAX_DISTANCE:
            top = min(self.top(), other.top())
            bottom = max(self.bottom(), other.bottom())
            left = min(self.left(), other.left())
            right = max(self.right(), other.right())
            pos = np.array([[left, top], [right, top], [right, bottom], [left, bottom]])
            if self.left() < other.left():
                text = self.txt + other.txt
            else:
                text = other.txt + self.txt
            logger.debug("我[%r]和[%r]水平合并成[%s]", self, other, text)
            return BBox(pos, text)
        return None

    # 我们的垂直相交比（相交部分除以框中高度比较小的那个，主要是考虑大小比例悬殊的情况），如果包含关系，值为1
    # 情况1：我们相距很远，直接为0
    # 情况1：我们相互包含，直接为1
    # 情况1：我们确实相交
    def vertical_overlay_ratio(self, other):
        my_y1 = self.pos[:, 1].min()
        my_y2 = self.pos[:, 1].max()
        his_y1 = other.pos[:, 1].min()
        his_y2 = other.pos[:, 1].max()

        # 情况1
        if self.vertical_distance(other) != 0: return 0  # 如果距离不为0，那么根本不相交，相交比为0

        # 情况2
        if my_y1 <= his_y1 and my_y2 >= his_y2: return 1  # 我包含你
        if his_y1 <= my_y1 and his_y2 >= my_y2: return 1  # 你包含我

        # 情况3
        cross_height1 = abs(my_y1 - his_y2)
        cross__height2 = abs(my_y2 - his_y1)

        y_height_ratio = min(cross_height1, cross__height2) / min(self.height(), self.height())
        return y_height_ratio

    # 我们的水平相交比（相交部分除以框中宽度比较小的那个，主要是考虑大小比例悬殊的情况），如果包含关系，值为1
    # 情况1：我们相距很远，直接为0
    # 情况1：我们相互包含，直接为1
    # 情况1：我们确实相交
    def horizontal_overlay_ratio(self, other):
        my_x1 = self.pos[:, 0].min()
        my_x2 = self.pos[:, 0].max()
        his_x1 = other.pos[:, 0].min()
        his_x2 = other.pos[:, 0].max()

        # 情况1
        if self.horizontal_distance(other) != 0: return 0  # 如果距离不为0，那么根本不相交，相交比为0

        # 情况2
        if my_x1 <= his_x1 and my_x2 >= his_x2: return 1  # 我包含你
        if his_x1 <= my_x1 and his_x2 >= my_x2: return 1  # 你包含我

        # 情况3
        cross_width1 = abs(my_x1 - his_x2)
        cross__width2 = abs(my_x2 - his_x1)

        y_width_ratio = min(cross_width1, cross__width2) / min(self.width(), self.width())
        return y_width_ratio

    def is_keybbox(self):
        return not self.field == None

    def is_the_pos(self, pos):
        return (self.pos == pos).all()

    def center(self):
        x = (self.pos[:, 0].min() + self.pos[:, 0].max()) / 2
        y = (self.pos[:, 1].min() + self.pos[:, 1].max()) / 2
        return (int(x), int(y))


# 尝试找到key的bbox们：
# - 1个字忽略
# - 2个字相同
# - 3个字以上必须编辑距离差1
# - 或者以key关键字开头
# key_type："key-value","table","key-value,table" 3种
def find_similar_key(text, key_type):
    text = text.strip()

    if (len(text)) <= 1:
        logger.debug("此文本只有一个字[%s]，怒略", text)
        return None

    # 数字、日期，直接忽略，肯定不是key啊
    if re.match("^[\/\-0-9]+$", text):
        logger.debug("此文本[%s]为数字/日期，怒略", text)
        return None

    #  TODO 包含的场景未来得考虑：关键字加在前文本和后文本之间的情况
    # found_field = None
    # for field in FEILDS:
    #     index = text.find(field['text'])
    #     if index==-1: continue
    #     found_field = field
    # if found_field:
    #     logger.debug("此文本[%s]包含key[%s]",text,found_field['text'])
    #     return found_field

    # 为了只识别有效字符，简化文本，去掉所有的标点符号
    import utils
    text = utils.ignore_symbol(text)

    # 大于等于3，就要找一个编辑距离最短的key
    min_el = 10000
    similar_field = None
    for field in FEILDS:

        key_type_list = key_type.split(",")
        if not field['type'] == key_type_list: continue

        # 如果长度是2，要精确匹配
        if (len(text)) == 2:
            if field['text'] == text:
                logger.debug("此文本[%s]长度为2，等于key[%s]", text, field['text'])
                return field
            continue  # 长度为2，又不是key，尝试下一个key

        if text.startswith(field['text']):
            logger.debug("此文本[%s]是以 key[%s]开头的", text, field['text'])
            return field

        # 长度大于等于3，要求和最接近的key的编辑距离距离要为1（条件暂时苛刻点）
        el = Levenshtein.distance(text, field['text'])
        if el < min_el:
            min_el = el
            similar_field = field
    if min_el <= 1:
        logger.debug("此文本[%s]最像[%s]，边界距离[%d]", text, similar_field, min_el)
        return similar_field

    logger.debug("此文本[%s]不像所有的key", text)
    return None


# 通过坐标找到bbox，我们认为坐标是唯一标识
def find_bbox_by_pos(bboxes, pos):
    for bbox in bboxes:
        if (pos == bbox.pos).all():
            return bbox
    return None


# 把bbox们转成位置数组pos们
def get_poses(bboxes):
    poses = []
    for bbox in bboxes:
        poses.append(bbox.pos)
    return np.array(poses)


# 按照pos的数组，去过滤掉bboxes
def filter_bboxes_by_poses(bboxes, poses):
    left_bboxes = []
    for _bbox in bboxes:
        for pos in poses:
            if _bbox.is_the_pos(pos):
                left_bboxes.append(_bbox)
                break
    logger.debug("总bboxes[%d]个，过滤poses[%d]个，过滤后剩余bboxes[%d]个", len(bboxes), len(poses), len(left_bboxes))
    return left_bboxes


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])
    # find_similar_key("投保人：刘创")
