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