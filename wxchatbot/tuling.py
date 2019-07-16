# coding: utf-8 
import requests
import sys

TULING_TOKEN = '7faa2fe104b549beaa08fba4de7d39c9'
url_api = 'http://www.tuling123.com/openapi/api'
msg = "如果你觉得很麻烦， 也可以暂时使用图灵机器人"


data = {
    'key'    : TULING_TOKEN,
    'info'   : msg, # 收到消息的文字内容
}
s = requests.post(url_api, data=data).json()
print (s) # 打印所获得的json查看如何使用
# {u'text': u'回复的内容', u'code': 100000}