# -*- coding:utf-8 -*-
import sys, pymysql, time, datetime, json, jieba, re, progressbar, codecs
import logging as logger, gensim
from bs4 import BeautifulSoup
from scipy.sparse import csc_matrix
import numpy as np
import pandas as pd
from jieba import analyse
from gensim import corpora, models, similarities
from sklearn.manifold import TSNE
from time import time
from sqlalchemy import create_engine
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from sklearn import manifold, datasets
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import NullFormatter
import matplotlib.patches as patches

df = pd.read_csv("chenjijun.csv")
groups = df.groupby("Customer")

recs = []

y = 0
for name, group in groups:
	y+= 20
	print name, "------------------\n"
	for key,value in group.iterrows():
		# print value['USF']
		# print value['UEF']
		xy = (int(value['USF']),y)
		width= int(value['UEF']) - int(value['USF'])
		height=20
		print xy,width,height
    	rect = patches.Rectangle(xy,width,height,linewidth=1,edgecolor='b',facecolor='none')
    	recs.append(rect)


fig, ax = plt.subplots(1)
plt.xlim((5000,15000))
plt.ylim((0,3500))
for rect in recs:
	ax.add_patch(rect)

plt.show()