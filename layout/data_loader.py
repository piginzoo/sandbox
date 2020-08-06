import os, cv2, json, numpy as np
from bbox import BBox


def load_data(path):
    input_dir = os.path.join(path, "input")
    output_dir = os.path.join(path, "output")

    image_names = os.listdir(input_dir)

    image_names=[]
    # image_names.append("32461594351366_.pic_hd.jpg")
    # image_names.append("国寿祥瑞终身寿险.jpg")
    # image_names.append("健康源（2019）增强版终身重大疾病保险..jpg")
    # image_names.append("国寿祥瑞终身寿险.jpg")
    # image_names.append("鑫盛12（996）.jpg")
    # image_names.append("百万守护重大疾病保险.jpg")
    # image_names.append("鑫利（936）.jpg")
    image_names.append("信泰爱驾宝两全保险.jpg")
    # image_names.append("工银安盛人寿御立方三号两全保险.jpg")
    # image_names.append("百万任我行（1149）.jpg")
    images = []
    all_pos = []
    all_txt = []
    all_bboxes = []

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
        bboxes = []
        for one in data:
            bbox_pos = []
            for d in one['pos']:
                pos = [int(d['x']), int(d['y'])]
                bbox_pos.append(pos)
            one_image_txt.append(one['word'])
            one_image_pos.append(bbox_pos)
            bboxes.append(BBox(bbox_pos, one['word']))
        all_txt.append(one_image_txt)
        all_pos.append(np.array(one_image_pos))
        all_bboxes.append(bboxes)

    return image_names, images, all_pos, all_txt, all_bboxes
