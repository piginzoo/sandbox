#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import sys
reload(sys)

if sys.getdefaultencoding() != 'utf-8':
	sys.setdefaultencoding('utf-8')
	reload(sys)

import imgkit



s="<!DOCTYPE html><html>\
<title></title><style type=\"text/css\">table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style><div><header><h1></h1></header>\
<body>\
<div><h3>预警说明：<font color=\"red\"> </font>转账订单，超过15分钟未处理，请关注。</h3>\
</body></html>"
imgkit.from_string(s, 'out.jpg',{'encoding': "UTF-8"})
