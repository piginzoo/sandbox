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
<div><h3>预警说明：<font color=\"red\">宜人贷</font>转账订单，超过15分钟未处理，请关注。</h3><h4>预留备注：请联系账务组同事关注转账订单数据。</h4><h4>统计时间为：2018-08-26 20:10:12 ~ 2018-08-26 19:55:12</h4><h4>总笔数：2条，举例如下。（按照入库时间升序排序）</h4><table><tbody><tr><th>序号</th><th>商户编码</th><th>商户名称</th><th>入库时间</th><th>商户订单号</th><th>结算交易单号</th></tr><tr><td>1</td><td>0000221</td><td>宜人贷</td><td>2018-08-26 19:51:19</td><td>4785475751</td><td>CEZ15Y20180826195119757352556174</td></tr><tr><td>2</td><td>0000221</td><td>宜人贷</td><td>2018-08-26 19:51:27</td><td>4785482117</td><td>CEZ15Y20180826195127681358922112</td></tr></tbody></table></div><br><div><p>【以下内容可忽略】 为定位报警系统问题预留，读取规则信息：<br>通知邮件发送时间[2018-08-26 20:10:21 802],<br></p></div></div>\
</body></html>"
imgkit.from_string(s, 'out.jpg',{'encoding': "UTF-8"})
