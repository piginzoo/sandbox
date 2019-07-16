# coding: utf-8 	
from wxpy import *
import sys
reload(sys) 
sys.setdefaultencoding('utf8')

tuling = Tuling(api_key='7faa2fe104b549beaa08fba4de7d39c9')
tuling.do_reply("今天天气如何？")

# 进入Python命令行，让程序保持运行
embed()