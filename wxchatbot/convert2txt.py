# coding: utf-8 	
from pydub import AudioSegment
from io import BytesIO

import logging as logger
import base64
import threading,urllib,urllib2,json,base64,hashlib,time

logger.basicConfig(
    level=logger.INFO,
    format="[%(levelname)s] %(message)s"
)

import logging

l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def _covert2text_baidu(audio):
    from aip import AipSpeech

    """ 你的 APPID AK SK """
    APP_ID = '11753660'
    API_KEY = 'CMVuH7x1lphsIn7eOXbLxG9H'
    SECRET_KEY = '9mCGRDqvF90Dv60zsvZ5ZPjMHsccBn6b'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    transform = client.asr(audio, 'wav',8000)
    print transform
    return transform['result'][0]

#调用科大讯飞，直接转成语音
def _covert2text(voice_data):
    
    base64_audio = base64.b64encode(voice_data)
    body = urllib.urlencode({'audio': base64_audio})

    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = 'ce1723f8e1ef9174d0849c63a97233d1'
    param = {"engine_type": "sms8k", "aue": "raw"}

    x_appid = '5ae1775b'
    x_param = base64.b64encode(json.dumps(param).replace(' ', ''))
    x_time = int(int(round(time.time() * 1000)) / 1000)
    x_checksum = hashlib.md5(api_key + str(x_time) + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib2.Request(url, body, x_header)
    result = urllib2.urlopen(req)
    result = result.read()
    logger.debug("科大讯飞转化的数据：%s",result)
    json_result = json.loads(result)
    print json_result['data']
    return json_result['data']


file = ['out.mp3']#'0.376393216371.data','0.106663749877.data','0.935259418886.data']
for name in file:
    with open(name, 'rb') as f:
        data = f.read()
        audio = AudioSegment.from_mp3(BytesIO(data))
        audio.export("out2.wav", format="wav")
        with open('out2.wav','rb') as f2:
            data = f2.read()
            print "百度："
            print _covert2text_baidu(data)
            print "讯飞："
            print _covert2text(data)
