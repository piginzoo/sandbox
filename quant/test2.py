import numpy as np
import pandas as pd

df = pd.DataFrame([
    ['2020-1-1','A',1.0],
    ['2020-1-1','A',1.00001],
    ['2020-1-1','B',2.0],
    ['2020-1-1','C',3.0],
    ['2020-1-2', 'A', 1.1],
    ['2020-1-2', 'B', 2.1],
    ['2020-1-2', 'C', 3.1],
    ['2020-1-3', 'A', 1.2],
    ['2020-1-3', 'B', 2.2],
    ['2020-1-3', 'C', 3.2]
],columns=['date','stock','value'])
df = df.set_index(['date','stock'])
df = df[~df.index.duplicated()]
df_new = df.unstack('stock')
print(df_new.info())

exit()

print("-------")
df = pd.read_csv("clvn.csv",)
df = df.set_index(['tradeDate','stkID'])
print(df.info())
df = df[~df.index.duplicated()]
print(df.unstack('stkID').info())

exit()

df1 = pd.DataFrame([
    ['2020-1-1','A',1.0],
    ['2020-1-1','B',2.0],
    ['2020-1-1','C',3.0],
],columns=['date','stock','value'])

df2 = pd.DataFrame([
    ['2020-1-1','A1',1.0],
    ['2020-1-1','B1',2.0],
    ['2020-1-1','C1',3.0],
],columns=['date1','stock1','value1'])

df1['stock1'] = df2.stock1
print(df1)

df1 = df1.set_index(['date','stock'])
print(df1)

df3 = df2.reset_index()
print(df2)
print(df3)
print(df3.date1)

df2.index = [1,10,100]
print(df2)
df4 = df2.reset_index()
print(df2)
print(df4)

import numpy as np
data = np.array([])
for i in range(10):
    data = np.append(data,np.array(['1','2','3']))
print(pd.DataFrame(data))

# python test2.py