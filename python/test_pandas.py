import pandas as pd 
dfs = [pd.DataFrame(list(range(20))) for i in range(4)]
df = pd.concat(dfs,axis=1)
df.columns = ['a','b','c','d']
# print(df)

dfs = [pd.DataFrame(list(range(20))) for i in range(3)]
df2 = pd.concat(dfs,axis=1)
df2.columns = ['a','f','g']
# print(df2)

df = df.reset_index(drop=True)
df2 = df2.reset_index(drop=True)

df['a1','b1','c1'] = df2
print(df)

