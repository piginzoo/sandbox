#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2, random, os, time, yaml, argparse,sys
from playsound import playsound
from aip import AipSpeech
from hashlib import md5
import json, requests
import urllib, random

AUDIO_APP_ID = ''
AUDIO_API_KEY = ''
AUDIO_SECRET_KEY = ''
TRANSLATE_APP_ID = ''
TRANSLATE_API_KEY = ''


# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def read(client, word):
    reader = random.choice([0, 1, 3, 4])
    result = client.synthesis(
        word,
        'zh',
        1, {
            'vol': 10,
            'per': reader
        })
    # print("调用百度合成完毕:%r,长度：",result,len(result))

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        if not os.path.exists("audios"):
            os.path.mkdir("audios")
        with open('audios/output.mp3', 'wb') as f:
            f.write(result)
        playsound('audios/output.mp3')


def translate(word):
    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang = 'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    try:

        salt = random.randint(32768, 65536)
        sign = make_md5(TRANSLATE_APP_ID + word + str(salt) + TRANSLATE_API_KEY)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': TRANSLATE_APP_ID, 'q': word, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        # Send request
        # print(payload)
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()

        # Show response
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        return result['trans_result'][0]['dst']
    except Exception as e:
        print(e)
        return "报错啦"


def load_cfg():
    f = open("key.yml", 'r', encoding='utf-8')
    result = f.read()
    config = yaml.load(result, Loader=yaml.FullLoader)
    f.close()
    sys.modules[__name__].AUDIO_APP_ID = config['audio_app_id']
    sys.modules[__name__].AUDIO_API_KEY = config['audio_api_key']
    sys.modules[__name__].AUDIO_SECRET_KEY = config['audio_secrete_key']
    sys.modules[__name__].TRANSLATE_APP_ID = config['translate_app_id']
    sys.modules[__name__].TRANSLATE_API_KEY = config['translate_app_key']


def main(book):
    if not os.path.exists(book):
        print("单词书不存在：", book)
        exit()

    load_cfg()

    words = []
    with open(book) as f:
        words = f.read()
        words = words.split(" ")

    random.shuffle(words)

    # print("语音配置：%s/%s/%s" % (AUDIO_APP_ID, AUDIO_API_KEY, AUDIO_SECRET_KEY))
    client = AipSpeech(AUDIO_APP_ID, AUDIO_API_KEY, AUDIO_SECRET_KEY)

    reviews = []
    go = True
    while go:
        print("一共%s个单词" % len(words))
        reviews = []
        for w in words:
            print("%s" % w)
            read(client, w)
            b = input("会否？(n)")
            if b == "n" or b == "N":
                r = translate(w)
                print("中文----> %s\n" % r)
                reviews.append(w)
        b = input("复习一遍了，%d个不会，退出(y)?" % len(reviews))
        if b == "y" or b == "Y":
            go = False
        words = reviews


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', '-b', type=str, default='books/words.txt')
    args = parser.parse_args()

    main(args.book)
