import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool
import table
import re
from row_parser import *
import Levenshtein
from debug import *
from fields import *
import utils


def test_process_bbox(text,key_type="key-value"):
    key_value_list,last_value_bbox =  process_bbox(BBox.create_virtual_bbox(text),key_type)
    return "Key/Value:{}, 上一个Key的Value:{}".format(key_value_list,last_value_bbox)

# 解析一个bbox，由于key可能存在连着value的情况，需要解析一下
#   "保险合同号:"
#   "保险合同号:500505958548"
#   "保险合同号:3939393939保险生效日：2020年09月08日"
#   "保险合同号:3939393939保险生效日：2020年09月08日货币单位"
#   "保险合同号:3939393939保险生效日：2020年09月08日货币单位：人民币"
#   "2020年3月4号保险合同号:...."   //[2020年3月4号]<--- 上一个key的value
def process_bbox(_bbox, key_type):
    bbox_text = _bbox.txt
    bbox_text = bbox_text.strip()

    if (len(bbox_text)) <= 1:
        logger.debug("此文本只有一个字[%s]，怒略", bbox_text)
        return None,BBox.create_virtual_bbox(bbox_text)

    # 数字、日期，直接忽略，肯定不是key啊
    if re.match("^[\/\-0-9]+$", bbox_text):
        logger.debug("此文本[%s]为数字/日期，怒略", bbox_text)
        return None,BBox.create_virtual_bbox(bbox_text)

    # 为了只识别有效字符，简化文本，去掉所有的标点符号
    text = utils.ignore_symbol(bbox_text)
    logger.debug("去除标点符号的文本：%s",text)

    # 先一口气找到所有的keys
    matched_fields = []
    for field in FEILDS:
        # 看此key是不是需要被check的对象
        key_type_list = key_type.split(",")
        if not field['type'] == key_type_list: continue # key的类型必须一致，如果是key-value,table，两个都得对上
        # 关键词在中间的（注意，可能有多个）
        pos = text.find(field['text'])
        if pos!=-1:
            logger.debug("发现了1个key:%s,pos:%d",field['text'],pos)
            matched_fields.append([field,pos])
    logger.debug("发现了%d个keys",len(matched_fields))

    # 挺长，但是确不包含任何key，都是value啊
    if len(matched_fields)==0:
        return None,BBox.create_virtual_bbox(bbox_text)

    # 去掉重复的，如"合同"和"保险合同"
    filtered_matched_fields = []
    for _field,pos in matched_fields:
        b_contained_by_other = False
        for _f,_ in matched_fields:
            if _field['text']==_f['text']:continue
            if _field['text'] in _f['text']:
                # 完蛋淘汰
                logger.debug("备选Key[%s]包含在Key[%s]中，舍弃", _field['text'] , _f['text'])
                b_contained_by_other = True
        if not b_contained_by_other:
            filtered_matched_fields.append([_field,pos])

    # 处理每个key
    #   "保险合同号:3939393939保险生效日：2020年09月08日货币单位"
    #   "保险合同号:3939393939保险生效日：2020年09月08日货币单位：人民币"
    #    ^                  ^                      ^
    key_values = []
    min_pos = 99999
    for i in range(len(filtered_matched_fields)):
        _matched_field,pos = filtered_matched_fields[i]
        if pos<min_pos: min_pos=pos

        if i+1 < len(filtered_matched_fields):
            _, next_pos = filtered_matched_fields[i+1]
        else:
            next_pos = len(text)
        logger.debug("从[%s]抽取一个key-value[%d->%d]:[%s]",text,pos,next_pos,text[pos:next_pos])
        key_value_text = text[pos:next_pos]
        _key_value = _process_one_key_text(_bbox,key_value_text,_matched_field)
        key_values.append(_key_value)

    # print("min_pos:",min_pos)
    if min_pos>0:
        last_value_bboxes = BBox.create_virtual_bbox(text[:min_pos])
    else:
        last_value_bboxes = None

    logger.debug("发现的key-values：%r",key_values)
    logger.debug("发现的属于上一个的value：%r", last_value_bboxes)
    return key_values, last_value_bboxes


from bbox import KeyValue,BBox
def _process_one_key_text(_bbox,text,field):

    logger.debug("处理1个bbox[%r],text[%s],field[%s]",_bbox,text,field['text'])
    # 恰好只有key
    if text==field["text"]:
        logger.debug("[%s]就是个单纯的key",text)
        return KeyValue(_bbox,field)

    field_len = len(field["text"])

    # 有key，有value
    key_bbox = BBox.create_virtual_bbox(field["text"]) # 先创建个虚拟的key_bbox
    value = text[field_len:] # 得到value文本
    # 去除冒号
    if len(value) > 0 and (value[0] == ":" or value[0] == "："):
        # 开头是个冒号啊
        logger.debug("去除了key后剩余的串[%s]是以冒号开头的啊",value)
        value = value[1:]
    value_bbox = BBox.create_virtual_bbox(value)
    logger.debug("最终的value是：%s",value)

    key_value=KeyValue(key_bbox,field,_bbox)
    key_value.append_value_box(value_bbox)
    return key_value

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    # logger.debug("保险合同号:")
    # logger.debug(test_process_bbox("保险合同号"))
    # logger.debug("保险合同号:500505958548")
    # logger.debug(test_process_bbox("保险合同号:500505958548"))
    # logger.debug("保险合同号:3939393939保险生效日：2020年09月08日")
    # logger.debug(test_process_bbox("保险合同号:3939393939保险生效日：2020年09月08日"))
    # logger.debug("保险合同号:3939393939保险生效日：2020年09月08日货币单位")
    # logger.debug(test_process_bbox("保险合同号:3939393939保险生效日：2020年09月08日货币单位"))
    # logger.debug("保险合同号:3939393939保险生效日：2020年09月08日货币单位：人民币")
    # logger.debug(test_process_bbox("保险合同号:3939393939保险生效日：2020年09月08日货币单位：人民币"))
    # logger.debug("2020年3月3号保险的合同号:500505958548")
    # logger.debug(test_process_bbox("2020年3月3号保险合同号:500505958548"))# 测试编辑距离为1的key
    logger.debug("交费方式:年交")
    logger.debug(test_process_bbox("交费方式:年交","key-value,table"))