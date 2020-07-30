import numpy as np
import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool
from fields import *

class BBox():
    def __init__(self, pos, txt):
        if type(pos)==list: pos = np.array(pos)
        assert pos.shape==(4,2)
        self.pos = pos
        self.txt = txt
        self.field = None

    def __str__(self):
        return self.pos.tolist()

    # 比比谁最靠上
    def __cmp__(self, other):
        my_y = self.pos[:,1].min()
        his_y = other[:,1].min()
        return my_y<his_y

    def edit_distance(self,text):
        return Levenshtein.distance(text, self.txt)

# 用来找key value
def find_similar_key(text):

    text = text.strip()

    if (len(text)) <= 1:
        logger.debug("此文本只有一个字[%s]，怒略", text)
        return None

    if re.match("^[\/\-0-9]+$", text):
        logger.debug("此文本[%s]为数字，忽略", text)
        return None

    # 如果长度是2，要精确匹配
    if (len(text)) == 2:
        for field in FEILDS:
            if field['text']==text:
                logger.debug("此文本[%s]包含key[%s]",text,field['text'])
                return field
        return None

    #  TODO 包含的场景未来得考虑
    # found_field = None
    # for field in FEILDS:
    #     index = text.find(field['text'])
    #     if index==-1: continue
    #     found_field = field
    # if found_field:
    #     logger.debug("此文本[%s]包含key[%s]",text,found_field['text'])
    #     return found_field

    # 大于等于3，就要找一个编辑距离最短的key
    min_el = 10000
    similar_field = None
    for field in FEILDS:
        if text.startswith(field['text']):
            logger.debug("此文本[%s]是以 key[%s]开头的",text,field['text'])
            return field

        el = Levenshtein.distance(text, field['text'])
        if el < min_el:
            min_el = el
            similar_field = field
    if min_el <= 2:
        logger.debug("此文本[%s]最像[%s]，边界距离[%d]", text, similar_field, min_el)
        return similar_field

    logger.debug("此文本[%s]不像所有的key",text)
    return None

def get_bbox_by_pos(bboxes, pos):
    for bbox in bboxes:
        if np.array_equal(pos, bbox.pos):
            return True
    return False


if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])
    find_similar_key("投保人：刘创")