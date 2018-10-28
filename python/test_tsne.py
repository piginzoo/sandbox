# !/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
from numpy.linalg import cholesky
import matplotlib.pyplot as plt

# 二维正态分布
sampleNo = 1000
mu = np.array([[1, 5]])
Sigma = np.array([[1, 0.5], [1.5, 3]])
R = cholesky(Sigma)
s = np.dot(np.random.randn(sampleNo, 2), R) + mu
plt.subplot(144)
# 注意绘制的是散点图，而不是直方图
plt.plot(s[:,0],s[:,1],'+')
plt.show()