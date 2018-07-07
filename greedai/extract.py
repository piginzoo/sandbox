#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import io,os
import sys,re
from bs4 import BeautifulSoup
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

files = os.listdir("rawdata")
# print files

def get_info(person_node):
	name_node = person_node.find('a',class_="turnto")
	name = name_node.get_text()

	info_node = person_node.find('td',class_="intro")
	info_text = info_node.get_text()
	age = re.sub("\D", "", info_text)

	sex = "不详"
	sex = "男" if info_text.find("男") != -1
	sex = "女" if info_text.find("女") != -1

	return name,age,sex

def parse_person_title(table):
	for row in table.find_all('tr'):
		names = row.find_all('td',class_="tc name")
		titles = row.find_all('td',class_="tl")
		#对于一行tr里面只有一个人的信息
		if len(names) == 0: continue
		if len(names) == 1:
			print get_name(names[0]) + "/" + titles[0].get_text() + "/" + get_age(names[0])
		#对于一行tr里面只有2个人的信息	
		if len(names) == 2:
			print get_name(names[0]) + "/" + titles[0].get_text()+ "/" + get_age(names[0])
			print get_name(names[1]) + "/" + titles[1].get_text()+ "/" + get_age(names[1])

def parse(content):
	soup = BeautifulSoup(content, "html.parser")
	# [script.extract() for script in soup.findAll('script')]
	# [style.extract() for style in soup.findAll('style')]
	table = soup.find('table', class_="m_table managelist m_hl")
	parse_person_title(table)


#参考data/000430.html
for file in files:
	with open("rawdata/"+file, "r") as f:
		lines = f.read()
		# print lines
		parse(lines)


# # coding:utf-8


# url = 'http://python123.io/ws/demo.html'
# r = requests.get(url)
# demo = r.text  # 服务器返回响应

# soup = BeautifulSoup(demo, "html.parser")
# """
# demo 表示被解析的html格式的内容
# html.parser表示解析用的解析器
# """
# print(soup)  # 输出响应的html对象
# print(soup.prettify())  # 使用prettify()格式化显示输出