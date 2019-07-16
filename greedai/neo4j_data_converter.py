#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import io,os
import sys,re
from bs4 import BeautifulSoup
import requests
import pandas as pd
reload(sys)
sys.setdefaultencoding('utf-8')

## TODO
# 1. ST label
# 2. relationship column

#参考https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/
#我们需要生成这几个文件：
#   “executive.csv”,
#               name:ID,sex,age,title
#   "stock.csv",
#               company_id:ID,name,:LABEL //给“公司”实体添加“ST”的标记，这个由LABEL来实现
#   "concept.csv",
#               name:ID
#   "industry.csv",
#               name:ID
#   "executive_stock.csv",
#               :START_ID,role,:END_ID
#   "stock_industry.csv",
#               :START_ID,:END_ID
#   "stock_concept.csv"。
#               :START_ID,:END_ID
# movieId:ID;title;year:int;:LABEL
# personId:ID;name;:LABEL
# :START_ID;role;:END_ID;:TYPE
# ---------------------
# 实体： 
# Company:	
#	stockId:ID;name;industry;:LABEL -->不用变化，直接可以用
# Person:
#	name:ID;sex;age:int
# Concept:
#	name:ID
# Industry:
#	name:ID
#
# 关系：
# --------------------
# Company-Person:
# 	:START_ID;relation;:END_ID;:TYPE
# Comapny-Concept:	
#	:START_ID;relation;:END_ID;:TYPE
# Comapny-Industry:	
#	:START_ID;relation;:END_ID;:TYPE
# Neo4j的关系例子：
#:START_ID,role,:END_ID,:TYPE
# keanu,"Neo",tt0133093,ACTED_IN
# keanu,"Neo",tt0234215,ACTED_IN
# laurence,"Morpheus",tt0234215,ACTED_IN
#1.生成stock.csv
df_executive_prep = pd.read_csv("prepdata/executive_prep.csv",dtype = {'name':str, 'sex':str,'age': float,'company_id':str,'title':str})
df_stock_concept_prep = pd.read_csv("prepdata/stock_concept_prep.csv",dtype = {'code':str, 'name':str,'c_name': str})
df_stock_industry_prep = pd.read_csv("prepdata/stock_industry_prep.csv",dtype = {'code':str, 'name':str,'c_name': str})


# Company:
#	stockId:ID;name;industry;:LABEL -->不用变化，直接可以用
def run():
    #股票信息
    # , code, name, c_name
    # 0, 600007, 中国国贸, 外资背景
    df_stock1 = df_stock_concept_prep[['code','name']]
    df_stock2 = df_stock_industry_prep[['code', 'name']]
    df_stock = pd.concat([df_stock1,df_stock2])
    df_stock = df_stock.drop_duplicates()
    df_stock.rename(columns={'code': 'code:ID'}, inplace=True)
    df_stock[':LABEL'] = df_stock['name'].apply(lambda x: "ST;Stock" if "ST" in x else "Stock")
    df_stock.to_csv("neo4jdata/stock.csv",index=False)


    #高管信息
    df_executive = df_executive_prep[['name','age','sex']]
    df_executive.rename(columns={'name': 'name:ID'},inplace=True)
    df_executive = df_executive.drop_duplicates() #删除重复行
    df_executive = df_executive.drop_duplicates(['name:ID'], keep="first") #删除重复的人名，本来年龄不同应该区别对待，但是比如都叫张三，那就该名称张三1，张三2，但是懒得搞了，直接删除掉
    df_executive[':LABEL'] = "Executive"
    df_executive.to_csv("neo4jdata/executive.csv",index=False)

    #股票概念
    df_concept = df_stock_concept_prep[['c_name']]
    df_concept = df_concept.drop_duplicates()
    df_concept.rename(columns={'c_name': 'c_name:ID'}, inplace=True)
    df_concept = df_concept.drop_duplicates("c_name:ID",keep="first")
    df_concept = df_concept[df_concept["c_name:ID"] != "次新股"]
    df_concept[':LABEL'] = "Concept"
    df_concept.to_csv("neo4jdata/concept.csv",index=False)

    #行业
    df_industry = df_stock_industry_prep[['c_name']]
    df_industry = df_industry.drop_duplicates()
    df_industry.rename(columns={'c_name': 'c_name:ID'}, inplace=True)
    df_industry = df_industry.drop_duplicates("c_name:ID", keep="first")
    df_industry[':LABEL'] = "Industry"
    df_industry.to_csv("neo4jdata/industry.csv",index=False)

    #executive_stock 股票-高管关系 #:START_ID,role,:END_ID,:TYPE
    df_executive_stock = df_executive_prep[['company_id','title','name']]
    df_executive_stock.rename(columns={'company_id': ':START_ID', 'title': 'executive', 'name': ':END_ID'}, inplace=True)
    df_executive_stock[':TYPE']= ":ACTED_IN"
    df_executive_stock.to_csv("neo4jdata/executive_stock.csv",index=False)


    #stock_industry 股票-行业关系
    df_stock_industry = df_stock_industry_prep[['code','c_name']]
    df_stock_industry.rename(columns={'code': ':START_ID', 'c_name': ':END_ID'},inplace=True)
    df_stock_industry['belong'] = "行业"
    df_stock_industry[':TYPE'] = ":ACTED_IN"
    df_stock_industry.to_csv("neo4jdata/stock_industry.csv",index=False)


    #stock_concept 股票-关系
    df_stock_concept = df_stock_concept_prep[['code','c_name']]
    df_stock_concept.rename(columns={'code': ':START_ID', 'c_name': ':END_ID'},inplace=True)
    df_stock_concept['concept'] = '概念'
    df_stock_concept[':TYPE']= ":ACTED_IN"
    df_stock_concept.to_csv("neo4jdata/stock_concept.csv",index=False)


if __name__=="__main__":
    run()