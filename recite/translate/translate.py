import argparse
import hashlib
import json
import os
import random
import time
import traceback
import uuid
from hashlib import md5

import requests
import yaml

appid = "20190403000284145"
appkey = 'rK_EIgLdpNHelFENTmoK'
from_lang = 'en'
to_lang = 'zh'
endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def translate_baidu(query, appid, appkey):
    """
    http://api.fanyi.baidu.com/product/113
    """
    salt = random.randint(32768, 65536)
    sign = make_md5(str(appid) + query + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    return result['trans_result'][0]['dst']


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    YOUDAO_URL = 'https://openapi.youdao.com/api'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def translate_youdao(q, app_key, app_secret):
    """
    https://ai.youdao.com/DOCSIRMA/html/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91/API%E6%96%87%E6%A1%A3/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1-API%E6%96%87%E6%A1%A3.html
    """
    data = {}
    data['from'] = '源语言'
    data['to'] = '目标语言'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = app_key + truncate(q) + salt + curtime + app_secret
    sign = encrypt(signStr)
    data['appKey'] = app_key
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"
    response = do_request(data)
    result = response.json()
    r1 = result['translation']
    r1 = ",".join(r1)

    if result.get('basic',None):
        r2 = result['basic']['uk-phonetic']
        r3 = result['basic']['us-phonetic']
        r4 = result['basic']['explains']
        r4 = "\n".join(r4)
    else:
        r2=r3=r4=""

    # print(response.content)
    if r2=="":
        chinese = "意思:{} \n".format(r1)
    else:
        chinese = "意思:{} \n发音: 英[{}] 美[{}] \n更多:\n{}".format(r1, r2, r3, r4)
    return chinese


def load_conf(engine, yaml_file="../key.yml"):
    f = open(yaml_file, "r", encoding="utf-8")
    conf = yaml.load(f.read())
    if engine == "baidu":
        return conf['baidu']['appid'], conf['baidu']['secret']
    if engine == "youdao":
        return conf['youdao']['appid'], conf['youdao']['secret']
    return None, None


def __load(txt):
    file = open(txt, "r", encoding="utf-8")
    lines = file.readlines()
    new_lines = []
    for line in lines:
        line = line.strip()
        if line == "": continue
        new_lines.append(line)

    # 翻译后的文件路径
    path, _ = os.path.splitext(txt)
    translate_file_path = path + "_translate.txt"

    return new_lines, translate_file_path


def main(txt, engine, app_id, app_secret):
    start = time.time()
    lines, translate_file_path = __load(txt)
    translate_file = open(translate_file_path, "w", encoding="utf-8")

    if engine == "baidu":
        translate = translate_baidu
        print("使用百度翻译")
    if engine == "youdao":
        translate = translate_youdao
        print("使用有道翻译")

    for line in lines:
        try:
            result = translate(line, app_id, app_secret)
            print("翻译：" + line)
            print(result)
            translate_file.write(line)
            translate_file.write("\n")
            translate_file.write(result)
            translate_file.write("\n\n")
        except Exception as e:
            traceback.print_exc()
            print("翻译%s时候出错：%s" % (line,str(e)))

    translate_file.close()
    end = time.time()

    print("翻译了%d个单词，耗时：%.2f秒" % (len(lines), end - start))


# python translate.py --txt test.txt --engine youdao
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--txt", type=str)
    parser.add_argument("--engine", type=str)
    args = parser.parse_args()

    if not os.path.exists(args.txt):
        print("单词文件不存在：%s", args.txt)
        exit()
    if args.engine != "baidu" and args.engine != "youdao":
        print("engine只能为baidu或者youdao")
        exit()

    app_id, app_secret = load_conf(args.engine)
    if app_id is None:
        print("加载app_id,app_secret失败")
        exit()

    print("加载了 app_id=%s,app_secret=%s" % (appid, app_secret))

    main(args.txt, args.engine, app_id, app_secret)
