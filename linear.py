#encoding=utf-8
import statsmodels.api as sm 
#最小二乘
from statsmodels.stats.outliers_influence import summary_table 
#获得汇总信息
import numpy as np
x=np.random.random((2000,20))
y=np.random.random((2000,3))
 
print "x=",x.shape,"y=",y.shape
regr=sm.OLS(y,x)
res=regr.fit() 

print res.summary()
# st, data, ss2 = summary_table(res, alpha=0.05) 
#置信水平alpha=5%，st数据汇总，data数据详情，ss2数据列名
# fitted_values = data[:,2]  
#等价于res.fittedvalues