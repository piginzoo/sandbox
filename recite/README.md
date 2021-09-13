# 我的背单词程序

实现了一个自己背单词用的小程式

## 使用方式

python recite.py --book <book_path>

例子：python recite.py --book books/words.txt

启动之前，需要配置好《[需要的配置](##需要的配置)》，即你的百度语音合成、百度翻译的相关账号（app_id,app_key,screte_key)

单词书格式超简单，每行一个英文单词即可	

## 实现原理

- 调用百度的翻译来翻译：https://fanyi-api.baidu.com/api/trans/product/apidoc
- 调用百度的语音合成来读单词： https://ai.baidu.com/ai-doc/SPEECH/Ik4nlz8l6

## 需要的配置

需要在当前目录下创建文件：

key.yml:

```

	# 百度语音合成
	audio_app_id: <your app id>
	audio_api_key: <your app key>
	audio_secrete_key: <your secrete_key>

	# 百度翻译
	translate_app_id: <your app id>
	translate_app_key: <your app key>

```

## 爬取中文意思
写了一个爬虫[/translate]，去爬取所有的单词的意思，这样，可以用一个英文列表，
可以快速得到中文列表，形成一个文件，方便背诵。

使用方法：
`python translate.py --txt test.txt --engine youdao`

需要一个配置文件[key.yml]： 
```
# 百度
baidu:
    appid: xxxxxxxxxxxx
    secret: xxxxxxxxxxxx
    
# 有道
youdao:
    appid: xxxxxxxxxxxx
    secret: xxxxxxxxxxxx
```
里面的appid啥的，需要去[百度](http://api.fanyi.baidu.com/product/113)和[有道](https://ai.youdao.com/DOCSIRMA/html/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91/API%E6%96%87%E6%A1%A3/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1-API%E6%96%87%E6%A1%A3.html)去申请