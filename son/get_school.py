#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import requests
from bs4 import BeautifulSoup

url = "https://www.bjeea.cn/html/gkgz/tzgg/2022/0717/82188.html"

strhtml = requests.get(url)
strhtml.encoding = 'utf-8'
html_doc = strhtml.text
# 创建一个BeautifulSoup解析对象
soup = BeautifulSoup(html_doc, "html.parser")
# 获取所有的链接
trs = soup.find_all('tr')

#"所有的链接"
for tr in trs:
   # import pdb;pdb.set_trace()
   tds = tr.find_all("td")
   print("学校[%s]: 分数%s" %(tds[2].get_text(), tds[5].get_text()))