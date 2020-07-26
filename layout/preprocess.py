import os, json, cv2, numpy as np, re, requests, base64, datetime


def nparray2base64(data):
    _, img_data = cv2.imencode('.jpg', data)
    return str(base64.b64encode(img_data), 'utf-8')


def base64_to_image(base64_code):
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.frombuffer(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

    return img


def call(url, post_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=post_data, headers=headers)
    r = response.text
    return json.loads(r)


def do_ocr(url, image):
    base64_images = nparray2base64(image)
    sid = datetime.datetime.now().strftime("%Y%m%d%H%S%f")[:-3]
    post_data = {
        "img": base64_images,
        "sid": sid,
        "biz_type": "02"
    }
    result = call(url, post_data)
    return result


def do_rotate(url, image):
    base64_images = nparray2base64(image)
    sid = datetime.datetime.now().strftime("%Y%m%d%H%S%f")[:-3]
    post_data = {
        "data": base64_images,
        "sid": sid,
        "do_verbose": False
    }
    # print(post_data)
    result = call(url, post_data)
    print(result)
    image_roate = base64_to_image(result['image'])
    print("调用完")
    return image_roate


def process(host):
    # 调用内部识别接口，先识别成txt的json
    input_dir = os.path.join("data", "raw")
    output_dir = os.path.join("data", "input")
    image_names = os.listdir(input_dir)

    for img_name in image_names:
        name, ext = os.path.splitext(img_name)
        if ext != ".jpg":
            print("图像不是jpg:%s", ext)
            continue

        image = cv2.imread(os.path.join(input_dir, img_name))
        image = do_rotate("http://ai.{}.corp/preprocess".format(host), image)
        json_data = do_ocr("http://ai.{}.corp//v2/ocr.ajax".format(host), image)

        output_image = os.path.join(output_dir, img_name)
        output_json = os.path.join(output_dir, name + ".txt")
        cv2.imwrite(output_image, image)
        with open(output_json) as f:
            f.write(json_data)
        print("处理完：%s", img_name)


if __name__ == "__main__":
    import sys

    host = sys.argv[1]
    print(host)
    if host == None:
        print("Usage: python prepross.py <hostname>")
        exit()

    process(host)
