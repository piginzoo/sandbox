#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import tushare as ts

df = ts.get_industry_classified() 
print df

# TODO 保存成"stock_industry_prep.csv
df.to_csv('prepdata/stock_industry_prep.csv')

df = ts.get_concept_classified()
print df

#  TODO 保存成“stock_concept_prep.csv”
df.to_csv('prepdata/stock_concept_prep.csv')