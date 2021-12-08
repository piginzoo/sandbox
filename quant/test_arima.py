import download
import utils
import pandas as pd
import numpy as np
from matplotlib.font_manager import FontProperties
from scipy import  stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
utils.init_log()
utils.load_conf('test')
# python -m test.test_arima
df_stat = download.main("stat", use_cache=True, date='2021-11-11', backdays=3)
df = df_stat[df_stat['MOD_TYPE']==11005]
df = df['SUCCESS_RATE']
font0=FontProperties()
df.reset_index()
df.plot(figsize=(12,8))
plt.show()

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
sm.graphics.tsa.plot_acf(df.values,lags=40,ax=ax1) # lags 表示滞后的阶数
ax2 = fig.add_subplot(212)
sm.graphics.tsa.plot_pacf(df.values,lags=40,ax=ax2)
plt.show()





# 模型1
arma_mod70 = sm.tsa.ARMA(df, (7, 0)).fit(disp=False)
print(arma_mod70.aic, arma_mod70.bic, arma_mod70.hqic)
# 模型2
arma_mod01 = sm.tsa.ARMA(df, (0, 1)).fit(disp=False)
print(arma_mod01.aic, arma_mod01.bic, arma_mod01.hqic)
# 模型3
arma_mod71 = sm.tsa.ARMA(df, (7, 1)).fit(disp=False)
print(arma_mod71.aic, arma_mod71.bic, arma_mod71.hqic)
# 模型4
arma_mod80 = sm.tsa.ARMA(df, (8, 0)).fit(disp=False)
print(arma_mod80.aic, arma_mod80.bic, arma_mod80.hqic)
# 模型5（只是为了示范，p和q随便取的）
arma_mod32 = sm.tsa.ARMA(df, (3, 2)).fit(disp=False)
print(arma_mod32.aic, arma_mod32.bic, arma_mod32.hqic)
# 最佳模型可以取aic最小的一个


# 模型检验
# 在指数平滑模型下，观察ARIMA模型的残差是否是平均值为0且方差为常数的正态分布（服从零均值、方差不变的正态分布），
# 同时也要观察连续残差是否（自）相关。

# 对ARMA(7,0)模型所产生的残差做自相关图
resid = arma_mod70.resid
fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid.values.squeeze(), lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
plt.show()


# 观察残差是否符合正态分布
# 这里使用QQ图，它用于直观验证一组数据是否来自某个分布，或者验证某两组数据是否来自同一（族）分布。
# 在教学和软件中常用的是检验数据是否来自于正态分布。
resid = arma_mod70.resid # 残差
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
fig = qqplot(resid, line='q', ax=ax, fit=True)
plt.show()

# Ljung-Box检验
# 略

# 模型预测
# 模型确定之后，就可以开始进行预测了，我们对未来十年的数据进行预测。

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.loc['2001':].plot(ax=ax)
fig = arma_mod70.plot_predict('2009', '2250', dynamic=True, ax=ax, plot_insample=False, alpha=0.05)
plt.show()
print(arma_mod70.summary())

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.loc['2001':].plot(ax=ax)
fig = arma_mod70.plot_predict('2009', '2250', dynamic=False, ax=ax, plot_insample=False, alpha=0.05)
plt.show()

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.loc['2001':].plot(ax=ax)
fig = arma_mod32.plot_predict('2091', '2100', dynamic=True, ax=ax, plot_insample=False)
print(arma_mod32.summary())
plt.show()

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.loc['2001':].plot(ax=ax)
fig = arma_mod32.plot_predict('2091', '2100', dynamic=False, ax=ax, plot_insample=False)
plt.show()

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.loc['2001':].plot(ax=ax)
fig = arma_mod32.plot_predict('2002', '2100', dynamic=False, ax=ax, plot_insample=False)
plt.show()