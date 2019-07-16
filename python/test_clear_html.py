#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup,NavigableString
#import config

#去除html中的标签和表格，用于qq中显示
#qq比较操蛋的是，无法发送图片信息
def clean_html(html):
	bs = BeautifulSoup(html)#, 'html.parser'
	body = bs.body

	return __clear(body)

line_elements = ['br','p','h1','h2','h3','h4','h5']

def __clear(parent_node):
	# return bs.prettify()
	content = ""
	print "[",parent_node,"]"
	#是纯文本节点
	if isinstance(parent_node, NavigableString):
		print "NavigableString:[",parent_node,"]"
		return parent_node.string

	if parent_node.name in line_elements:
		content += "\n"

	children = parent_node.contents

	for child in children:
		if child.name == "table":
			content += parse_table(child)
		else:
			content += __clear(child)

	return content


def parse_table(tab):
	content = "\n"
	line = 0

	for tr in tab.findAll('tr'):

		#if line > config.monitor_max_table_line:break
		if line > 10:break

		content += "|"
		for td in tr.findAll('th'):
			content += td.getText().strip() + "|"
		for td in tr.findAll('td'):
			content += td.getText().strip() + "|"
		content = content + "\n"

		line += 1
	content = content + "...\n"
	return content


if __name__ == '__main__':
	with open("test_clear_html.html") as f:
		content = f.read()
		#print content
		print clean_html(content)