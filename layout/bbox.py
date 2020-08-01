import re
from row_parser import *
import Levenshtein
from debug import *
from fields import *


class KeyValue():
    def __init__(self, key_bbox):
        self.value_boxes = []
        self.key_bbox = key_bbox
        self.process_key(key_bbox)

    # 由于key可能存在连着value的情况，需要解析一下
    def process_key(self, key_bbox):
        field = key_bbox.field
        assert field is not None
        key_text = key_bbox.txt

        if key_text == field['text']: return # 相等不处理

        # 剥离key中可能包含的values，形成一个虚拟Bbox
        key_index = key_text.find(field['text'])
        if key_index!=-1:
            left_text = key_text[key_index+len(field['text']):]
            if len(left_text) > 0 and (left_text[0] == ":" or left_text[0] == "："):
                left_text = left_text[1:]
            logger.debug("从keybox中分离出value:%s",left_text)
            self.value_boxes.append(BBox(np.zeros((4, 2)), left_text))

    def append_value_box(self, value):
        if type(value) == list:
            self.value += value
        assert type(value) == BBox
        self.value_boxes.append(value)

    def __to_string(self):
        value = "".join([bbox.txt for bbox in self.value_boxes])
        return "[%s] %s".format(self.key, value)

    def __str__(self):
        return self.__to_string()

    def __repr__(self):
        return self.__to_string()

    def __eq__(self, other):
        return self.key_bbox == other.key_bbox

class BBox():
    def __init__(self, pos, txt):
        if type(pos) == list: pos = np.array(pos)
        assert pos.shape == (4, 2)
        self.pos = pos
        self.txt = txt
        self.field = None

    def __str__(self):
        return self.txt #+ " " + str(self.pos.tolist())

    def __repr__(self):
        return self.txt #+ " " + str(self.pos.tolist())

    def __eq__(self, other):
        # 如果自己本身就是个无效坐标（虚拟bbox），就跟谁也不相同
        if (self.pos == 0).all():
            logger.debug("我是一个虚拟bbox")
            return False
        if (self.pos == other.pos).all():
            logger.debug("other[%s]和我[%s]相等",other.txt,self.txt)
            return True
        return False

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

    # 我们的垂直相交比
    def vertical_overlay_ratio(self, other):
        my_y1 = self.pos[:, 1].min()
        my_y2 = self.pos[:, 1].max()
        his_y1 = other.pos[:, 1].min()
        his_y2 = other.pos[:, 1].max()
        y_height1 = abs(my_y1 - his_y2)
        y_height2 = abs(my_y2 - his_y1)
        y_height_ratio = min(y_height1, y_height2) / max(y_height1, y_height2)
        return y_height_ratio


    def is_keybbox(self):
        return not self.field==None

    def is_the_pos(self,pos):
        return (self.pos == pos).all()


# 尝试找到key的bbox们：
# - 1个字忽略
# - 2个字相同
# - 3个字以上必须编辑距离差1
# - 或者以key关键字开头
def find_similar_key(text):
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


    # 为了只识别有效字符，简化文本
    import utils
    text = utils.ignore_symbol(text)

    # 大于等于3，就要找一个编辑距离最短的key
    min_el = 10000
    similar_field = None
    for field in FEILDS:

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
    assert pos.shape == (4, 2), pos.shape
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
def filter_bboxes_by_poses(bboxes,poses):
    left_bboxes = []
    for bbox in bboxes:
        for pos in poses:
            if bbox.is_the_pos(pos):
                left_bboxes.append(bbox)
                break
    logger.debug("总bboxes[%d]个，过滤poses[%d]个，过滤后剩余bboxes[%d]个",len(bboxes),len(poses),len(left_bboxes))
    return left_bboxes




if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])
    # find_similar_key("投保人：刘创")
