# coding: utf-8 	
from wxpy import *

# 设置默认的level为DEBUG
# 设置log的格式
import logging as logger
logger.basicConfig(
    level=logger.INFO,
    format="[%(levelname)s] %(message)s"
)

# bot = Bot()
bot = Bot(cache_path=True)
tuling = Tuling(api_key='7faa2fe104b549beaa08fba4de7d39c9')

import sys
class ExceptionHook:
	instance = None
	def __call__(self, *args, **kwargs):
		if self.instance is None:
			from IPython.core import ultratb
			self.instance = ultratb.FormattedTB(mode='Plain',color_scheme='Linux', call_pdb=1)
		return self.instance(*args,**kwargs)

sys.excepthook = ExceptionHook()


jy = bot.groups().search(u'咱们仨')
print(jy)
jy = jy[0]
print("找到：%s"%jy)

from threading import current_thread
thread = current_thread()
print thread.getName()

@bot.register(jy,run_async=False)
def print_message(msg):
	print "-------------"
	xxxxx
	print(msg.text)
	tuling.do_reply(msg)

# 进入Python命令行，让程序保持运行
embed(shell='python')