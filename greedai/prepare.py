#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import io,os
import sys,re
from bs4 import BeautifulSoup
import requests

reload(sys)
sys.setdefaultencoding('utf-8')


#解析一个table里面的一个关于人的那个DOM节点，
#会返回某个人的 职位、名字、性别
def get_info(person_node):
	name_node = person_node.find('a',class_="turnto")
	name = name_node.get_text()
	name = name.replace(","," ")


	info_node = person_node.find('td',class_="intro")
	info_text = info_node.get_text()
	age = re.sub("\D", "", info_text)

	sex = "不详"
	if info_text.find("男") != -1: sex = "男" 
	if info_text.find("女") != -1: sex = "女" 

	return name,age,sex

#解析一个table
#会返回这个表里的所有的人的信息
def parse_person_title(table):

	list = []
	if( table is None): return list
	for row in table.find_all('tr'):
		names = row.find_all('td',class_="tc name")
		titles = row.find_all('td',class_="tl")
		#对于一行tr里面只有一个人的信息
		if len(names) == 0: continue
		if len(names) == 1:
			
			name,age,sex = get_info(names[0])
			title = titles[0].get_text()
			title = title.replace(",","、")
			#print name+"/"+age+"/"+sex+"/"+title
			list.append({'name':name,'age':age,'sex':sex,'title':title})

		#对于一行tr里面只有2个人的信息	
		if len(names) == 2:

			name,age,sex = get_info(names[0])
			title = titles[0].get_text()
			title = title.replace(",","、")
			#print name+"/"+age+"/"+sex+"/"+title
			list.append({'name':name,'age':age,'sex':sex,'title':title})

			name,age,sex = get_info(names[1])
			title = titles[0].get_text()
			title = title.replace(",","、")
			#print name+"/"+age+"/"+sex+"/"+title
			list.append({'name':name,'age':age,'sex':sex,'title':title})
 	return list

#解析一个文件
def parse(content):
	list = []
	soup = BeautifulSoup(content, "html.parser")
	table = soup.find('table', class_="m_table managelist m_hl")
	list = list + parse_person_title(table)
	return list

files = os.listdir("rawdata")
# print files

list = []
#参考data/000430.html
for file in files:
	with open("rawdata/"+file, "r") as f:
		content = f.read()
		company_id = file[0:file.find(".")]
		# print content
		#解析一个 html文件
		one_company_list = parse(content)
		for one_person in one_company_list:
			one_person_full_info = {
				'company_id': company_id,
				'name': one_person['name'],
				'sex': one_person['sex'],
				'title': one_person['title'],
				'age': one_person['age']
			}
			list.append(one_person_full_info)

result_file = open("prepdata/executive_prep.csv","w")

result_file.write('name,sex,age,company_id,title')
result_file.write("\n")

for one in list:
	result_file.write(one['name'])
	result_file.write(",")
	result_file.write(one['sex'])
	result_file.write(",")
	result_file.write(one['age'])
	result_file.write(",")
	result_file.write(one['company_id'])
	result_file.write(",")
	result_file.write(one['title'])
	result_file.write("\n")				

result_file.close()
