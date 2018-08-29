#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
 
# s.encode('gb18030')#this will be compile error
import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


#s = '@老六 中文中文中文中文中文'  # 注意这里的 str 是 str 类型的，而不是 unicode 
#start  = s.find("@")
#end  = s.find(" ",start)
#print s[end:].strip()

#s = '中文中文中文中文中文@老六'  # 注意这里的 str 是 str 类型的，而不是 unicode 
#start  = s.find("@")
#print s[:start]

def remove_at_unicode(msg):
	print "orignal:%s" % msg
	msg = msg.strip()
	start = msg.find("@")
	print "start=%d" % start
	if start==0:
		end = msg.find(" ",start)
		print "end=%d" % end 
		return msg[end:].strip()
	else:
		return msg[:start].strip()


def remove_at(msg):
	print "orignal:%s" % msg
	msg = msg.strip()
	start = msg.find("@")
	print "start=%d" % start
	if start==0:
		end = msg.find(" ",start)
		print "end=%d" % end 
		return msg[end:].strip()
	else:
		return msg[:start].strip()

print remove_at('@老六 中文中文中文中文中文1234567890')
print remove_at('中文中文中文中文中文1 @老六1')


print remove_at_unicode(u'@昵称 你好yes!!!')
print remove_at_unicode("@昵称 你好yes!!!")
print remove_at_unicode(u" @昵称你好yes!!!")
print remove_at_unicode(u"你好yes!!! @昵称")
