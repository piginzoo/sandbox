# coding: utf-8
import os
import csv

'''
解析type5_train.csv并且得到对应的识别码和他的长度
'''
filename = os.path.join(os.getcwd(), 'type5_train.csv')
if os.path.exists(filename):
	with open(filename, 'r') as f:
	  reader = csv.reader(f)
	  for item in reader:
	    print item[1],len(item[1])#识别码
