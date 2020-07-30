#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import md5
import urllib
import random

appid = '20190403000284145' #你的appid
secretKey = 'rK_EIgLdpNHelFENTmoK' #你的密钥



def translate(word):
    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)

    sign = appid+word+str(salt)+secretKey
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+urllib.quote(word)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    try:
        
        response = requests.get('api.fanyi.baidu.com'+myurl)
        # infirmary:{"from":"en","to":"zh","trans_result":[{"src":"infirmary","dst":"\u533b\u52a1\u5ba4"}]}
        return json.loads(response.text['trans_result'][0]['dst'])
    except Exception as e:
        print(e)
        return "报错啦"
    finally:
        if httpClient:
            httpClient.close()


words = []    
with open("words.txt") as f:
    words = f.read()
    words = words.split(" ")

random.shuffle(words)

reviews = []
go = True
while go:
    print("一共%s个单词" % len(words))
    reviews = []
    for w in words:
        r = translate(w)
        print("%s" % w)
        b = raw_input("会否？(n)")
        print("%s\n" % r)
        if b=="n" or b=="N":
            reviews.append(w)
    b = raw_input("复习一遍了，%d个不会，退出(y)?" %  len(reviews))
    if b=="y" or b=="Y":
        go = False
    words = reviews        
