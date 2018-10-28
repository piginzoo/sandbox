# coding: utf-8 	
from wxpy import *
from pydub import AudioSegment
from io import BytesIO
from aip import AipSpeech
import logging as logger
import traceback,sys,base64
import threading,urllib,urllib2,json,base64,hashlib,time

logger.basicConfig(
    level=logger.DEBUG,
    format="[%(levelname)s] %(message)s"
)
reload(sys)
if sys.getdefaultencoding() != 'utf-8':
        sys.setdefaultencoding('utf-8')
        reload(sys)

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
def _covert2text_xunfei(voice_data):
    
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



# bot = Bot()
bot = Bot(cache_path=False)

groups = bot.groups().search(u'testbot')
group = groups[0]
print("找到群组：%r"%group)

from threading import current_thread
thread = current_thread()
print thread.getName()

@bot.register(group,run_async=False)
def print_message(msg):
    if msg.type == "Recording":
        try:

            raw_data = msg.get_file()
            with open('out.mp3','wb') as f1:
                f1.write(raw_data)
            logger.debug("消息格式为声音，使用科大讯飞转化")
            audio = AudioSegment.from_mp3(BytesIO(raw_data))
            audio.export("out.wav", format="wav")
            result = u""
            with open('out.wav','rb') as f2:
                data = f2.read()
                result += "百度："
                result +=_covert2text_baidu(data)
                result += "\n讯飞："
                result += _covert2text_xunfei(data)
                logger.info(result)
                msg.reply(result)
        except Exception as e :
            traceback.print_exc()
            return "error:"+str(e)
    elif msg.type =="TEXT":
    	logger.debug("文本消息：%s",msg.text)
    elif msg.type!="TEXT":
        logger.error("消息格式不正确：%s",msg.type)
        return "消息格式不正确"

# 进入Python命令行，让程序保持运行
embed(shell='python')