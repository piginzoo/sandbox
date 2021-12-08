# coding: utf-8

# 第一个因子:
# clv: close location value,
# ( (close-day_low) - (day_high - close) ) / (day_high - day_low)
# 这玩意，是一个股票的，每天都有，是一个数，
# 我们要从一堆的股票N只中，得到N个这个值，可以形成一个截面，
# 用这个截面，我们可以拟合出β和α，
# 然后经过T个周期（交易日），就可以有个T个β和α，
# 因子长这个样子：
# tradeDate
#  	      	000001.XSHE  000002.XSHE
# 2019-01-02  -0.768924    0.094851     。。。。。
# 。。。。。。
# 类比gpd、股指（市场收益率），这个是因子不是一个啊？而是多个股票N个啊？咋办？
# 
# 参考：https://www.bilibili.com/read/cv13893224?spm_id_from=333.999.0.0

# In[ ]:

# 取1个股票1天的行情数据（用前复权的 ）
DataAPI.MktEqudAdjGet(secID=u"",ticker=u"600276",tradeDate=u"",beginDate=u"20190101",endDate=u"20211101",isOpen="",
                      field=u"secID,tradeDate,openPrice",pandas="1")


# 取多个股票的某天的因子（智飞生物300122，招商证券600999，招商蛇口001979，青岛中程300208，大参林603233，恒瑞医药600276）
# 截面数据

# In[ ]:

DataAPI.MktStockFactorsOneDayGet(tradeDate=u"20150227",
                                  secID=u"",
                                  ticker=u"300122,600999,001979,300208,603233,600276",
                                  field=u"secID,tradeDate,openPrice,DAVOL5",pandas="1")


# 取一只股票的一段时间的因子

# In[ ]:

DataAPI.MktStockFactorsDateRangeGet(secID=u"",ticker=u"000001",beginDate=u"20170612",endDate=u"20170616",field=u"",pandas="1")


# 真实因子，CLV，计算多个股票的多天的因子

# 取日期间的交易日和股票池

# In[ ]:

date_list = DataAPI.TradeCalGet(exchangeCD=u"XSHG,XSHE",beginDate=u"20190101",endDate=u"20211101",
                                isOpen=u"1",field=u"",pandas="1")
date_list= date_list[date_list['isOpen']==1]['calendarDate'].values.tolist()
date_list
universeD = DynamicUniverse('HS300')
universeD


# In[ ]:

import time
import pandas as pd
import numpy as np
def CLV(universe, begin, end, file_name):
    # 计算收盘价在k线的位置
    count = 0
    secs_time  = 0
    start_time = time.time()
    
    N = 50
    factor = pd.DataFrame()
    # 每支股票
    for stk in universe:
        # 得到日交易数据
        data = DataAPI.MktEqudAdjGet(secID=stk,
                                     beginDate=begin,
                                     endDate=end,
                                field='secID,tradeDate,closePrice,highestPrice,lowestPrice,openPrice,preClosePrice')
        # data.info()
        tmp_factor_data = data.sort('tradeDate')
        # 计算CLV因子
        tmp_factor_data['CLV'] = (             (tmp_factor_data['closePrice'] - tmp_factor_data['lowestPrice']) -              (tmp_factor_data['highestPrice'] - tmp_factor_data['closePrice']))/             (tmp_factor_data['highestPrice'] - tmp_factor_data['lowestPrice'])
        # 处理出现一字涨跌停
        tmp_factor_data.loc[(tmp_factor_data['highestPrice']==tmp_factor_data['lowestPrice']) &                             (tmp_factor_data['openPrice'] > tmp_factor_data['preClosePrice']),'CLV'] = 1 
        tmp_factor_data.loc[(tmp_factor_data['highestPrice']==tmp_factor_data['lowestPrice']) &                             (tmp_factor_data['openPrice'] < tmp_factor_data['preClosePrice']),'CLV'] = -1 
        
        tmp_factor_data = tmp_factor_data[['tradeDate','CLV']]
        tmp_factor_data.columns = ['tradeDate',stk]
        
        if factor.empty:
            factor = tmp_factor_data
        else:
            factor = factor.merge(tmp_factor_data, on='tradeDate', how='outer')
            
        # 打印进度部分
        count+=1
        if count>0 and count % N ==0:
            finish_time = time.time()
            print(count,)
            print('\t'+str((np.round(finish_time-start_time)-secs_time,0)) + ' seconds elapsed')
            secs_time = (finish_time - start_time)
    factor.to_csv(file_name)
    return factor
                         


# 开始计算CLV		

# In[ ]:

begin_date = '20190101'
end_date = '20211201'

universe = set_universe('HS300')
universe = universe[:50]

# 开始日~结束日，50只股票，计算这个因子，这个因子是，每天对应1个股票1个数，比如 2019-1-2，000001.XSHE股票，对应一个因子值，
# 这个值，不是收益率。
CLV(universe=universe, begin= begin_date, end = end_date, file_name='CLV.csv')


# In[ ]:

import pandas as pd
CLVfactor = pd.read_csv('CLV.csv')
CLVfactorstack = CLVfactor.set_index(['tradeDate'])
CLVfactorstack = CLVfactorstack.stack() # 按照tradeDate，变成一个树状结构
CLVfactorstack.hist(figsize=(12,6), bins=50)


# 去极值和标准化方法

# In[ ]:

def winsorize_series(se):
    q = se.quantile([0.025, 0.975])
    if isinstance(q, pd.Series) and len(q) == 2:
        se[se < q.iloc[0]] = q.iloc[0]
        se[se > q.iloc[1]] = q.iloc[1]
    return se

def standardize_series(se):
    se_std = se.std()
    se_mean = se.mean()
    return (se - se_mean)/se_std


# In[ ]:

factor_init = CLVfactorstack.groupby(level='tradeDate').apply(winsorize_series)# 去极值
factor_init = factor_init.groupby(level='tradeDate').apply(standardize_series)# 标准化
factor_init.hist(figsize=(12,6), bins=50)


# 3. 中性化（可选）
# 3.1 中性化的优点：能够将新因子的已知部分剥离掉，剩下的部分为真正新的因子，这样我们能够真正看明白新因子是否真正是新的，还是仅仅原有因子的线性组合加噪音。
# 3.2 中性化的缺点：计算复杂，每一个新因子都要进行一次中性化。作为基准的老因子之间，比如行业和市值因子之间也有相关性。
# 3.3 中性化计算步骤：
# - 确定将目标因子进行中性化的因子（市值因子，行业因子等等）
# - 将目标因子做为因变量，将市值因子，行业因子做为自变量
# - 运行回归，将回归的残差项做为中性化后的因子

# In[ ]:

import time
import numpy as np
import DataAPI
import pandas as pd

# 3.4 实操代码

# 3.4.1计算市值因子

def getMarketValueAll(universe, begin, end, file_name):
    # 获取股票历史每日市值

    print('MarketValue will be calculated for ' + str(len(universe)) + ' stocks:')

    count = 0
    secs_time = 0
    start_time = time.time()
    N = 50
    ret_data = pd.DataFrame()
    for stk in universe:
        data = DataAPI.MktEqudAdjGet(secID=stk, beginDate=begin, endDate=end,field='secID,tradeDate,negMarketValue')  # 拿取数据
        tmp_ret_data = data.sort('tradeDate')

        # 市值部分
        tmp_ret_data = tmp_ret_data[['tradeDate', 'negMarketValue']]
        tmp_ret_data.columns = ['tradeDate', stk]
        if ret_data.empty:
            ret_data = tmp_ret_data
        else:
            ret_data = ret_data.merge(tmp_ret_data, on='tradeDate', how='outer')

        # 打印进度部分
        count += 1
        if count > 0 and count % N == 0:
            finish_time = time.time()
            print(count,)
            print('   ' + str(np.round((finish_time - start_time) - secs_time, 0)) + ' seconds elapsed.')
            secs_time = (finish_time - start_time)

    ret_data.to_csv(file_name)

    return ret_data


# 获取股票历史每日市值

# comnbinedfactor因子数据，是每天，多只股票
# 
#     tradeDate	stkID	     CLV	        MVfactor_std
# 0	2019-01-02	000001.XSHE	-7.689243e-01	4.530452
# 1	2019-01-02	000002.XSHE	9.485095e-02	4.530452
# 2	2019-01-02	000004.XSHE	-5.652174e-01	-0.428141
# 3	2019-01-02	000005.XSHE	-5.000000e-01	-0.376903
# 4	2019-01-02	000006.XSHE	-3.382353e-01	-0.226704
# 5	2019-01-02	000007.XSHE	-7.142857e-02	-0.388427
# 6	2019-01-02	000008.XSHE	4.000000e-01	-0.120089
# 7	2019-01-02	000009.XSHE	-4.677419e-01	-0.147528
# 8	2019-01-02	000010.XSHE	-7.401487e-15	-0.417451
# 
# Y= βX + e
# CLV = β * MV + e
# 我们不关心β，我们只关心e，e就是新的因子。
# 注意，这里是每只股票的这两个值做回归，比如有50只股票，那就是50个值对做回归，
# 就得到了每天，这个因子（被MV市值中性化后的CLV）的值。
# 因子是每天一个值，而且，是每个股票一个值，这个有点和我想想的不一样了，不是因子是共通的么？
# 我理解应该是每天1个值，类比于市场因子（比如股指的收益率）

# In[ ]:

import time
import pandas as pd
import statsmodels.api as sm
import numpy as np

begin_date = '20190101'  # 开始日期
end_date = '20211201'  # 结束日期
universe = set_universe('HS300')  # 股票池
universe = universe[0:50]  # 计算速度缓慢，仅以部分股票池作为sample
# ----------- 计算股票流通市值 ----------------

print('=======================')
start_time = time.time()
MVfactor = getMarketValueAll(universe=universe, begin=begin_date, end=end_date, file_name='marketvalue.csv')
finish_time = time.time()

# ----------- 去极值和标准化 ----------------
MVfactor = MVfactor.set_index(['tradeDate'])
MVfactorstack = MVfactor.stack()
MVfactor_init = MVfactorstack.groupby(level='tradeDate').apply(winsorize_series)  # 去极值
MVfactor_std = MVfactor_init.groupby(level='tradeDate').apply(standardize_series)  # 标准化
MVfactor_std.hist(figsize=(12, 6), bins=50)

# 3.4.5进行因子中性化
# 将个股收益率和因子对齐
comnbinedfactor = pd.concat([CLVfactorstack, MVfactor_std], axis=1, join='inner')
comnbinedfactor = comnbinedfactor.reset_index()
comnbinedfactor.columns = ['tradeDate', 'stkID', 'CLV', 'MVfactor_std']

# 按天进行回归，回归残差作为新因子
CLVneutralizedfactor = pd.DataFrame()
unidate = comnbinedfactor.reset_index().tradeDate.drop_duplicates()
unidate = list(unidate)
for d in unidate:
    
    # 按照每一天去做回归，过滤出的tempdata，是某一天的所有股票的，'stkID'不同
    tempdata = comnbinedfactor.loc[comnbinedfactor['tradeDate'] == d, :]

    # print(">>>>>>>>>>>>>>>>>>>>>")
    # print("Calculate Date:",d)
    # print(tempdata.CLV)
    # print(tempdata.MVfactor_std)
    # print("<<<<<<<<<<<<<<<<<<<<")

    # MV:MarketValue:流通市值，
    model = sm.OLS(np.array(tempdata.CLV), np.array(tempdata.MVfactor_std))
    results = model.fit()
    CLVneutralizedfactor = CLVneutralizedfactor.append(pd.DataFrame(results.resid))
CLVneutralizedfactor['tradeDate'] = comnbinedfactor.tradeDate
CLVneutralizedfactor['stkID'] = comnbinedfactor.stkID
CLVneutralizedfactor = CLVneutralizedfactor.set_index(['tradeDate', 'stkID']) # 联合主键，日期+股票

# print("old columns:",CLVneutralizedfactor.columns)
# CLVneutralizedfactor.info()
CLVneutralizedfactor.columns = ['CLVneutralizedfactor'] # 中性因子，是每个股票每天1个
CLVneutralizedfactor


# In[ ]:

comnbinedfactor


# In[ ]:

import time
def getForwardReturns(universe, begin, end, window, file_name):
    """
    每天都计算一下从当日，到当日+5日后的收益率，所以最后5天没有值
    """
    # 计算个股历史区间前瞻回报率，未来windows天的回报率
    print('计算%d只股票的%d天的回报率' % (len(universe), window))
    count = 0
    secs_time = 0
    start_time = time.time()

    N = 50
    ret_data = pd.DataFrame()
    for stock in universe:
        data = DataAPI.MktEqudAdjGet(secID=stock,
                                     beginDate=begin,
                                     endDate=end,
                                     field='secID,tradeDate,closePrice')
        tmp_ret_data = data.sort('tradeDate')

        # 计算历史窗口的前瞻收益率
        tmp_ret_data['forwardReturns'] = tmp_ret_data['closePrice'].shift(-window) / tmp_ret_data['closePrice'] - 1.0
        tmp_ret_data = tmp_ret_data[['tradeDate','forwardReturns']]
        tmp_ret_data.columns = ['tradeDate',stock]

        if ret_data.empty:
            ret_data = tmp_ret_data
        else:
            ret_data = ret_data.merge(tmp_ret_data)

    ret_data.to_csv(file_name)
    print("保存5天因子收益率到文件：",file_name)
    return ret_data


# In[ ]:

begin_date = '20190101'  # 开始日期
end_date = '20211201'  # 结束日期
universe = set_universe('HS300')  # 股票池
universe = universe[0:50]  # 计算速度缓慢，仅以部分股票池作为sample
window_return = 5
forward_5d_return_data = getForwardReturns(
        universe=universe,
        begin=begin_date,
        end=end_date,
        window=window_return,
        file_name="ForwardReturns_W5_Rtn.csv"
    )


# """
# IC法
# 1.确定持仓周期，我们这里是5天
# 2.计算每天股票对应的未来调仓周期的收益
# 3.计算未来调仓周期收益率和因子收益率之间的相关系数
# """
# 

# In[ ]:

import pandas as pd
import numpy as np
import statsmodels as st
# 计算每天的clv收益率和之后5天的股票收益率的秩的相关系数
ic_data = pd.DataFrame(index=CLVfactor.index,columns=['IC','pValue'])

# 计算相关系数
index = 1
for date in ic_data.index:
    tmp_illiq = CLVfactor.ix[date]
    tmp_ret = forward_5d_return_data.ix[date]
    corr = pd.DataFrame(tmp_illiq)
    ret =  pd.DataFrame(tmp_ret)
    corr.columns = ['corr']
    ret.columns = ['ret']
    corr['ret'] = ret['ret']
    # corr = corr[~np.isnan(corr['corr'])][~np.isnan(corr['ret'])]
    # if len(corr)<5:
    #     continue
    ic,p_value = st.spearman(corr['corr'],corr['ret']) # 计算秩相关系数 Rank_IC
    ic_data['IC'][date] = ic
    ic_data['pValue'][date] = p_value
    index+=1
    print("finish Rank_IC/spearman for date: %r, %d/%d", %(date,index,len(ic_data)))

print("IC mean：%.4f" % ic_data['IC'].mean())
print("IC median：%.4f" % ic_data['IC'].median())
print("IC %d>0, %d<0" % (ic_data[ic_data.IC>0], ic_data[ic_data.IC<0]))


# In[ ]:

# 给每天的CLV,5日收益率,秩相关系数做图
ic_data = ic_data.dropna()
fig = plt.figure(figsize=(16,6))
ax1 = fig.add_subplot(111)
lns1 = ax1.plot(np.array(ic_data.IC),lable='IC')

lns = lns1
labs = [l.get_label() for l in lns]
ax1.legend(lns,labs,bbox_to_anchor=[0.5,0.1],
           loc='',mode='',borderaxespad=0.,
           fontsize=12)
ax1.set_xlabel("相关系数",fontproperties=font,fontsize=16)
ax1.set_ylabel("日期",fontproperties=font,fontsize=16)
ax1.set_title("CLV和之后5日收益的秩的相关系数",fontproperties=font,fontsize=16)
ax1.grid()


# In[ ]:

# 计算IC方法二
forward_5d_return_datastack = forward_5d_return_data.stack()
combineMatrix = pd.concat([CLVfactorstack,forward_5d_return_datastack],axis=1,join='inner')
combineMatrix.columns=['CLV','FiveDayfwdRtn']
DayIC = combineMatrix.groupby(level='tradeDate').corr(method='spearman')
DayIC = DayIC.reset_index().drop(['level_1'],axis=1)
DayIC = pd.DataFrame(DayIC.loc[DayIC.CLV!=1,'CLV'])
DayIC.columns=['IC']
print("IC的均值：%.4f" % DayIC.mean())
print("IC的中位数：%.4f" % DayIC.median())
print("IC值%d个>0, %d个<0" % (DayIC[DayIC.IC>0], DayIC[DayIC.IC<0]))


# """
# # 回归法
# 1.首先将因子和未来收益率在界面上对齐（日期、代码）
# 2.将未来的收益率作为因变量，因子作为自变量，回归计算出来的系数作为因子收益率
# 3.计算因子收益率的t值等相关统计量
# """
# 

# In[ ]:

combineMatrix = combineMatrix.reset_index()
combineMatrix.columns = ['tradeDate','stockID','CLV','FiveDayfwdRtn']
# 按天回归，回归系数作为因子收益率
unidate = combinefactor.reset_index().tradeDate.drop_duplicates()
unidate = list(unidate)
CLVFactorRtn = pd.DataFrame(columns=['CLVfactorRtn','t_values'],index=unidate)
for d in unidate:
    tempdata = combineMatrix.loc[combineMatrix['tradeDate']==d,:]
    tempdata = tempdata.dropna()
    if len(tempdata)>0:
        model = sm.OLS(np.array(tempdata.FiveDayfwdRtn),
                       np.array(tempdata.CLV))
        results = model.fit()
        CLVFactorRtn.loc[d,'CLVfactorRtn'] = results.params[0]
        CLVFactorRtn.loc[d, 't_values'] = results.tvalues[0]

    """
    回归法因子检测
    1.计算t值绝对值的均值，看t值是不是显著不为0，有效性是>2
    2.t值绝对值大于2的比例-稳定性(比例大于40%)
    3.计算因子收益率的时间序列上的t值,是不是显著不为0 -- 风险因子？alpha因子？
    """
    # 1.计算t值绝对值的均值，看t值是不是显著不为0，--- 有效性
    print("t_value 绝对均值:" % (CLVFactorRtn.tvalues.abs().mean()))
    # 2.t值绝对值序列大于2的比例 --- 稳定性
    print("正IC的百分比: %.2f" % len(CLVFactorRtn[CLVFactorRtn.tvalues.abs()>2]/float(len(CLVFactorRtn))))
    # 3.计算因子收益率的时间序列上的t值,是不是显著不为0 -- 风险因子？alpha因子？
    print("因子收益率均值 %.4f" % CLVFactorRtn.CLVfactorRtn.mean())
    print("因子收益率t值 %.4f" % CLVFactorRtn.CLVfactorRtn.mean()/CLVFactorRtn.CLVfactorRtn.std())


# In[ ]:

# 画图
fig = plt.figure(figsize=(16,6))
ax1 = fig.add_subplot(111)
lns1 = ax1.plot(np.array(CLVFactorRtn.CLVfactorRtn.cumsum()),lable='IC')

lns = lns1
labs = [l.get_label() for l in lns]
ax1.legend(lns,labs,
           bbox_to_anchor=[0.5,0.1],
           loc='',
           ncol=3,
           mode='',
           borderaxespad=0.,
           fontsize=12)
ax1.set_xlabel("收益率",fontproperties=font,fontsize=16)
ax1.set_ylabel("日期",fontproperties=font,fontsize=16)
ax1.set_title("CLV收益率累计",fontproperties=font,fontsize=16)
ax1.grid()
"""
这个有正、有负，说明其是风险因子，而不是alpha因子，
"""


# In[ ]:

# 分层法检测

n_quantile = 10
# 统计十分位数
cols_mean = [i+1 for i in range(n_quantile)]
cols = cols_mean

excess_returns_means =pd.DataFrame(index=CLVfactor.index,columns=cols)

# 计算ILLIQ分组的超额收益平均值
for date in excess_returns_means.index:
    qt_mean_results = []

    # 去ILLIQ中的nan
    tmp_CLV = CLVfactor.ix[date].dropna()
    tmp_return = forward_5d_return_data.ix[date].dropna()
    tmp_return_mean = tmp_return.mean()

    pct_quantiles = 1.0/n_quantile
    for i in range(n_quantile):
        down = tmp_CLV.quantile(pct_quantiles*i)
        up = tmp_CLV.quantile(pct_quantiles*(i+1))
        i_quantile_index = tmp_CLV[(tmp_CLV<=up) & (tmp_CLV>down)].index
        mean_tmp = tmp_return[i_quantile_index].mean()- tmp_return_mean
        qt_mean_results.append(mean_tmp)

    excess_returns_means.ix[date] = qt_mean_results

excess_returns_means.dropna(inplace=True)
excess_returns_means.tail()


# In[ ]:

# 画图
fig = plt.figure(figsize=(16,6))
ax1 = fig.add_subplot(111)
excess_returns_means_dist = excess_returns_means.mean()
excess_dist_plus = excess_returns_means_dist[excess_returns_means_dist>0]
excess_dist_minus = excess_returns_means_dist[excess_returns_means_dist<0]

lns2 = ax1.bar(excess_dist_plus.index,excess_dist_plus.values, align='center',color='r',width=0.35)
lns3 = ax1.bar(excess_dist_minus.index,excess_dist_plus.values, align='center',color='r',width=0.35)

ax1.set_xlim(left=0.5,right=len(excess_returns_means_dist)+0.5)
ax1.set_ylim(-0.008,0.008)
ax1.set_ylabel("超额收益",fontproperties=font,fontsize=16)
ax1.set_xlabel("十分位分组",fontproperties=font,fontsize=16)
ax1.set_xticks(excess_returns_means_dist.index)
ax1.set_xticklabels([int(x) for x in ax1.get_xticks()],fontproperties=font,fontsize=14)
ax1.set_yticklabels([str(x*100)+"0%" for x in ax1.get_yticks()],fontproperties=font,fontsize=14)
ax1.set_title("ILLIQ因子超额收益率",fontproperties=font,fontsize=16)
ax1.grid()


# 
# # 下面我们使用有矿里面的回测模块使用因子讲股票分组回测
# 
# # 可编辑部分和strategy模式一样，其余部分按本例代码编写即可
# 

# In[ ]:

# ---- 回测参数，可编辑 ----
start = '20190101'
end = '20211201'
benchmark = 'zz500'             # 策略参考基准
universe = set_universe('HS300')# 股票池
capital_base = 100000           # 投资资金
freq = 'd'                      # 使用日线进行回测
refresh_rate = 5                # 调仓频率, 表示执行handle_data的时间间隔

CLV_dates = CLVfactor.index.values

# 把回测参数封装到SimulationParameters中，供quick_backtest使用
sim_params = quartz.SimulationParameters(start,end,benchmark,universe,capital_base)
# 获取回测行情数据
idxmap,data =quartz.get_backtest_data(sim_params)
# 运行结果
results_illiq = {}

# 调整参数(选取股票的ILLIQ因子五分位数，进行快速回测
for quantile_five in range(1,6):

    # ---- 策略逻辑部分 ----
    commission = Commission(0.0002,0.0002)

    def initialize(account):
        pass

    def handle_data(account): # 单个交易日买入卖出
        pre_date = account.previous_date.strftime("%Y-%m-%d")
        if pre_date not in CLV_dates: # 只在计算过ILLIQ因子的交易日调仓
            return

        # 拿取调仓日前一个交易日的CLV因子，并按照相应的无分位选择股票
        pre_illiq = CLVfactor.ix[pre_date]
        pre_illiq = pre_illiq.dropna()

        pre_illiq_min = pre_illiq.quantile((quantile_five-1)*0.2)
        pre_illiq_max  = pre_illiq.quantile(quantile_five*0.2)
        my_univ =  pre_illiq[pre_illiq>=pre_illiq_min][pre_illiq<pre_illiq_max].index.values

        # 调仓逻辑
        univ = [x for x in my_univ if x in account.universe]

        # 不在股票池，清仓
        for stock in account.valid_secpos:
            if stock not in univ:
                order_to(stock,0)
        # 在目标股票池中，等权买入
        for stock in univ:
            order_pct_to(stock,1.01/len(univ))

    # 把回测逻辑封装到 TradeStrategy中，供quick_backtest调用
    strategy = quartz.TradingStrategy(initialize,handle_data)
    # 回测部分
    bt,acct = quartz.quick_backtest(sim_params,strategy,idxmap,data,refresh_rate,commission)

    # 对于回测的结果，可以通过 perf_parse 计算风险指标
    perf = quartz.perf_parse(bt,acct)

    tmp = {}
    tmp['bt'] = bt
    tmp['annualized_return'] = perf['annualized_return']
    tmp['volatility'] =perf['volatility']
    tmp['max_drawdown'] =perf['max_drawdown']
    tmp['alpha'] =perf['alpha']
    tmp['beta'] =perf['beta']
    tmp['sharp'] =perf['sharp']
    tmp['information_ratio'] =perf['information_ratio']

    results_illiq[quantile_five] = tmp