from __future__ import division
def fun(stockRet,factorOriginal,date,groupNum=5,groupPeriod=21,regressPeriod=120):
#    circulateMkv流通市值数据暂时没有，先用等权处理组合内收益
#    groupPeriod调仓周期；regressPeriod回归回溯周期
#    1,2,..,N组,多空组合,市场平均组合    
    #from imp import reload
    import scipy.io as sio  
    import factor_Standardized;#reload(factor_Standardized)
    import singleFactor_RegValidity;#reload(singleFactor_RegValidity)
    import maxDrawDown;#reload(maxDrawDown)
    import math;import numpy as np
    import pylab
    factor=factor_Standardized.fun(factorOriginal)
    #(mStockRet,nStockRet)=stockRet.shape
    mStockRet = stockRet.shape[0]
    nStockRet = stockRet.shape[1]
    groupStockIdx=dict.fromkeys(range(groupNum))
    nav=np.ones([mStockRet,groupNum+2]) 
    factorTvalueTS=np.ones(mStockRet)*np.nan
    i0=regressPeriod+2;
    for i in np.arange(i0-1,mStockRet):
        factorTvalueTS[i]=factorTvalueTS[i-1] #T日收盘后重新计算因子方向，T+1日开盘调仓
        if np.isnan(factorTvalueTS[i])==False and factorTvalueTS[i]!=0:
            for j in range(groupNum):
                nav[i,j]=nav[i-1,j]*(1+np.nanmean(stockRet[i,groupStockIdx[j]]))	
            nav[i,groupNum]=nav[i-1,groupNum]*(1+np.nanmean(stockRet[i,groupStockIdx[0]])-np.nanmean(stockRet[i,groupStockIdx[groupNum-1]]))			
            nav[i,groupNum+1]=nav[i-1,groupNum+1]*(1+np.nanmean(stockRet[i,]))	
        else:
            nav[i,]=nav[i-1,]        
        if i%groupPeriod==(i0-1)%groupPeriod:        
            try:
                [factorTvalue,factorRegValidity]=singleFactor_RegValidity.fun(stockRet[np.arange(i-regressPeriod,i+1),],factor[np.arange(i-regressPeriod,i+1),])
            except:
                factorTvalue=-1
            factorTvalueTS[i]=factorTvalue;		
            #factor[i,np.where(np.logical_or(tradeAmount[i,]==0, np.isnan(tradeAmount[i,])==True))]=np.nan#成交量为0或nan的股票不能买入
            if factorTvalue!=0 and np.isnan(factorTvalue)==False:
                factorTvalue=-1
                if factorTvalue>0:
                    factorSort=np.sort(-factor[i,])#np.sort 默认升序排列，nan在最后
                    factorSortIdx=np.argsort(-factor[i,])
                elif factorTvalue<0:                
                    factorSort=np.sort(factor[i,])#np.sort 默认升序排列，nan在最后
                    factorSortIdx=np.argsort(factor[i,])                
                firstNanIdx=np.where(np.isnan(factorSort)==True)[0][0]
                factorSortIdx=factorSortIdx[:firstNanIdx]
                inGroupNum=int(round(len(factorSortIdx)/groupNum))#每组股票数
                for j in range(groupNum-1):
                    groupStockIdx[j]=factorSortIdx[inGroupNum*j:inGroupNum*(j+1)]
                groupStockIdx[groupNum-1]=factorSortIdx[inGroupNum*(groupNum-1):]		
    		
    #画图
    # import matplotlib.pyplot as plt
    # for j in range(groupNum+2):
    #     pylab.plot_date(date,nav[:,j],linestyle='-')
    # label = [u'第1组',u'第2组',u'第3组',u'第4组',u'第5组',u'第1组减第5组',u'所有A股等权组合']
    # plt.legend(label)
    # plt.title(u'分五组回测资产曲线')
    # plt.show()
    
    #收益统计
    annualizedRet=np.ones(groupNum+2)*np.nan
    mdd=np.ones(groupNum+2)*np.nan
    sharpe=np.ones(groupNum+2)*np.nan
    winRate=np.ones(groupNum+2)*np.nan
    for j in range(groupNum+2):
        freq=12;
        annualizedRet[j]=(nav[-1,j]/nav[0,j])**(freq/mStockRet)-1;
        mdd[j]=maxDrawDown.fun(nav[:,j]);
        sharpe[j]=np.mean(np.diff(nav[:,j])/nav[0:-1,j])/np.std(np.diff(nav[:,j])/nav[0:-1,j])*math.sqrt(freq); 
        winRate[j]=np.count_nonzero(np.diff(nav[:,j])/nav[0:-1,j]>0)/(len(date)-1)
    
    backTestResult={}
    backTestResult['annualizedRet']=annualizedRet
    backTestResult['maxDrawDown']=mdd
    backTestResult['sharpe']=sharpe
    backTestResult['winRate']=winRate
    
    return backTestResult,nav
