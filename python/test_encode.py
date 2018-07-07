#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
s = '中文'  # 注意这里的 str 是 str 类型的，而不是 unicode 
# s.encode('gb18030')#this will be compile error
import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

with io.open("stories.md", "r") as f:
    lines = f.readlines()
    print lines
