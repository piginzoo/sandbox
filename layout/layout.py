import os, json, cv2, numpy as np, re
from row_parser import *
import Levenshtein
from debug import *
import points_tool

FEILDS = [
    "保单号",
    "保险单编号",
    "合同号",
    "险种名称",
    "合同签订日期",
    "合同生效日期",
    "签发地点",
    "缴费方式",
    "通讯地址（投保人地址）",
    "邮政编码",
    "开户行",
    "银行账号",
    "币种",
    "合同签发地",
    "首期保费合计(首期缴费)",
    "保单机构",
    "代理人",
    "投保人",
    "投保人信息",
    "姓名",
    "性别",
    "出生日期",
    "证件号码",
    "被保人信息",
    "与投保人关系",
    "身故受益人",
    "收益顺序",
    "收益份额",
    "险种名称",
    "基本保险额度",
    "标准保险费",
    "加费",
    "交费方式",
    "交费期间",
    "保险期间",
    "满期日",
    "保费合计"]


# 用来找key value
def find_key_value(texts, pos):
    for text in texts:

        if (len(text)) <= 1:
            continue

        if re.match("\d+", text):
            # logger.debug("文本[%s]为数字",text)
            continue

        if (len(text)) == 2:
            for field in FEILDS:
                if text == field:
                    logger.debug("找到匹配文本：%s", field)
                    continue
            # logger.debug("找到匹配字段：%s", text)
            continue

        min_el = 10000
        similar_field = ""
        for field in FEILDS:
            el = Levenshtein.distance(text, field)
            if el < min_el:
                min_el = el
                similar_field = field
        if text.strip() == "": continue
        if min_el <= 2:
            logger.debug("此文本[%s]最像[%s]，边界距离[%d]", text, similar_field, min_el)


def get_by_pos(pos_origin, texts, pos):
    assert pos.shape == (4, 2)
    pos = pos.sort(axis=0)
    for po in pos_origin:
        assert po.shape == (4, 2)
        po = po.sort(axis=0)
        if np.array_equal(pos, po): return True
    return False


# 处理一张图
def process(image, pos):
    logger.debug("此图bboxes们：%r", pos.shape)
    left_data, avarage_row_heigt, exclued_data = exclude_1sigma(pos)
    # [N,x,y]
    height = pos[:, :, 1].max()  # 所有bbox的最大的y
    width = pos[:, :, 0].max()  # 所有bbox的最大的x
    logger.debug("图像最高：%d", height)
    rows, row_elements = recognize_row(left_data, height)
    rows, row_elements = split_high_row(rows, row_elements, avarage_row_heigt)
    logger.debug("最终切分出%d行rows和%d行row_elements", len(rows), len(row_elements))

    image = debug(image, rows, width, pos, exclued_data, abnormal_data=None)
    return image


def load_data(path):
    input_dir = os.path.join(path, "input")
    output_dir = os.path.join(path, "output")

    image_names = os.listdir(input_dir)
    images = []
    all_pos = []
    all_txt = []

    for img_name in image_names:
        image = cv2.imread(os.path.join(input_dir, img_name))
        images.append(image)

        name, ext = os.path.splitext(img_name)
        # logger.debug(img_name,name, "/",ext)
        json_path = os.path.join(output_dir, name + ".txt")
        json_data = open(json_path).read()
        data = json.loads(json_data)
        data = data['prism_wordsInfo']

        one_image_pos = []
        one_image_txt = []
        for one in data:
            bbox_pos = []
            for d in one['pos']:
                pos = [int(d['x']), int(d['y'])]
                bbox_pos.append(pos)
            one_image_txt.append(one['word'])
            one_image_pos.append(bbox_pos)
        all_txt.append(one_image_txt)
        all_pos.append(np.array(one_image_pos))

    return images, all_pos, all_txt

# TODO：矩形识别旋转的算法大bug

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])

    images, raw_pos, all_text = load_data("data")

    # 保留
    # original_pos = all_horizontal_pos.copy()

    for i in range(len(raw_pos)):

        one_image_horizontal_pos = []
        for pos in raw_pos[i]:
            rotated_pos = points_tool.rotate_rect_to_horizontal(pos)
            one_image_horizontal_pos.append(rotated_pos)
        one_image_pos = np.array(one_image_horizontal_pos)

        image = process(images[i], one_image_pos)

        # cv2.polylines(image, raw_pos[i], isClosed=True, color=(255, 0, 0), thickness=1)
        # cv2.polylines(image, one_image_pos, isClosed=True, color=(0, 0,255), thickness=1)
        # find_key_value(all_text[i],all_pos[i])
        print("--------------------------------------------------------")
        cv2.imwrite("debug/{}.jpg".format(i), image)
