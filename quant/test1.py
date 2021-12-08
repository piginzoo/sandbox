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
        data = DataAPI.MktEqudAdjGet(secId=stock,
                                     beginDate=begin,
                                     endDate=end,
                                     filed='secID,tradeDate,closePrice')
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

"""
IC法
1.确定持仓周期，我们这里是5天
2.计算每天股票对应的未来调仓周期的收益
3.计算未来调仓周期收益率和因子收益率之间的相关系数
"""

import pandas as pd
import numpy as np
import statsmodels as st
# 计算每天的clv收益率和之后5天的股票收益率的秩的相关系数
ic_data = pd.DataFrame(index=CLVfactor.index,columns=['IC','pValue'])

# 计算相关系数
for date in ic_data.index:
    tmp_illiq = CLVfactor.ix[date]
    tmp_ret = forward_5d_return_data.ix[date]
    corr = pd.DataFrame(tmp_illiq)
    ret =  pd.DataFrame(tmp_ret)
    corr.columns = ['corr']
    ret.columns = ['ret']
    corr['ret'] = ret['ret']
    corr = corr[~np.isnan(corr['corr'])][~np.isnan(corr['ret'])]
    if len(corr)<5:
        continue
    ic,p_value = st.spearman(corr['corr'],corr['ret']) # 计算秩相关系数 Rank_IC
    ic_data['IC'][date] = ic
    ic_data['pValue'][date] = p_value

print("IC的均值：%.4f" % ic_data['IC'].mean())
print("IC的中位数：%.4f" % ic_data['IC'].median())
print("IC值%d个>0, %d个<0" % (ic_data[ic_data.IC>0], ic_data[ic_data.IC<0]))

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

"""
# 回归法
1.首先将因子和未来收益率在界面上对齐（日期、代码）
2.将未来的收益率作为因变量，因子作为自变量，回归计算出来的系数作为因子收益率
3.计算因子收益率的t值等相关统计量
"""

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


# 下面我们使用有矿里面的回测模块使用因子讲股票分组回测

# 可编辑部分和strategy模式一样，其余部分按本例代码编写即可

# ---- 回测参数，可编辑 ----
start = '2020-1-1'
end = '2021-12-1'
benchmark = 'zz500'             # 策略参考基准
universe = set_universe('A')    # 股票池
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


