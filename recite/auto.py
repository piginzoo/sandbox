#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import http.client
import hashlib
import urllib
import random
import time

appid = '20190403000284145' #你的appid
secretKey = 'rK_EIgLdpNHelFENTmoK' #你的密钥

#http://api.fanyi.baidu.com/api/trans/product/desktop

def translate(word):
    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)

    sign = appid+word+str(salt)+secretKey
    m1 = hashlib.md5()
    m1.update(bytes(sign,encoding='utf-8'))
    sign = m1.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+urllib.parse.quote(word)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    try:
        
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        #response是HTTPResponse对象
        response = httpClient.getresponse()
        # infirmary:{"from":"en","to":"zh","trans_result":[{"src":"infirmary","dst":"\u533b\u52a1\u5ba4"}]}
        result = json.loads(response.read())
        print(result)
        return result['trans_result'][0]['dst']
    except Exception as e:
        print (e)
        return "报错啦"
    finally:
        if httpClient:
            httpClient.close()


words = []    
with open("_list.txt") as f:
    words = f.readlines()

t_file = open("list.txt","w")
i = 0
for w in words:
    w = w.strip()
    if w=="": continue
    t = translate(w)
    t_file.write(w)
    t_file.write("\t")
    t_file.write(t)
    t_file.write("\n")
    i+=1
    print("完成了：",w,"=>",t,",合计：",str(i))
    time.sleep(1)
t_file.close()
print("全部完成！！！")