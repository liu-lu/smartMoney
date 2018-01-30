import os  
from imp import reload
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pylab
from scipy import stats
os.chdir('D:/guo/quant/SmartMoney')
#提取数据
stockRetDF= pd.read_excel('QandReturns.xlsx', sheetname=u'收益率')
Qdf=pd.read_excel('QandReturns.xlsx', sheetname='Q')
stockRetDF=stockRetDF/100
Qdf[(Qdf==-2)|(Qdf==-1 )]=np.nan
date=stockRetDF.index;code=stockRetDF.columns
stockRet=stockRetDF.as_matrix();Q=Qdf.as_matrix()
#stockRet=stockRet[39:77,]#13年4月到16年5月
#Q=Q[39:77,]
#date=date[39:77]
#参数设置
groupNum=5
#1.因子rankIC月度序列
rankIC=[]
for i in range(Q.shape[0]-1):
    X=Q[i,]    
    Y=stockRet[i+1,]
    nanIdx=np.union1d(np.where(np.isnan(Y)==True)[0],np.where(np.isnan(X)==True)[0])
    rankIC.append(stats.spearmanr(np.delete(X,nanIdx),np.delete(Y,nanIdx))[0])
pylab.plot_date(date[0:-1],rankIC)
plt.title(u'Q因子RankIC月度序列')
plt.show()
pd.DataFrame(rankIC,index=date[0:-1],columns=['rankIC']).to_excel('rankIC.xlsx')
pd.DataFrame(np.nanmean(Q,axis=1),index=date,columns=['averageIC']).to_excel('averageIC.xlsx')

#2.检验Q因子有效性
factorOriginal=Q
import singleFactor_RegValidity;reload(singleFactor_RegValidity)
[factorTvalue,factorRegValidity]=singleFactor_RegValidity.fun(stockRet,factorOriginal)
#3.Q因子分组回测
groupPeriod=1;regressPeriod=1
dateNumber=range(stockRet.shape[0])
import singleFactor_GroupBacktest;reload(singleFactor_GroupBacktest)
idx2013=np.where(date.year==2013);idx2014=np.where(date.year==2014)
idx2015=np.where(date.year==2016);idx2016=np.where(date.year==2016)
backTestResult2013=singleFactor_GroupBacktest.fun(stockRet[idx2013,],factorOriginal[idx2013,],date[idx2013],groupPeriod=groupPeriod,regressPeriod=regressPeriod)
backTestResult2014=singleFactor_GroupBacktest.fun(stockRet[idx2014,],factorOriginal[idx2014,],date[idx2014],groupPeriod=groupPeriod,regressPeriod=regressPeriod)
backTestResult2015=singleFactor_GroupBacktest.fun(stockRet[idx2015,],factorOriginal[idx2015,],date[idx2015],groupPeriod=groupPeriod,regressPeriod=regressPeriod)
backTestResult2016=singleFactor_GroupBacktest.fun(stockRet[idx2016,],factorOriginal[idx2016,],date[idx2016],groupPeriod=groupPeriod,regressPeriod=regressPeriod)

#4剔除市值、动量、行业因素
mvDF=pd.read_excel('QandReturns.xlsx', sheetname=u'市值')
industryDF=pd.read_excel('QandReturns.xlsx', sheetname=u'行业')
mvDF[mvDF==0]=np.nan

mv=mvDF.as_matrix()
mv=mv[39:77,]
#分组平均函数
def group(factorX,factorY,groupNum):#Q是factorX,mv或动量是factorY    
    factorGroup=np.zeros([factorY.shape[0],groupNum])
    for i in range(factorY.shape[0]):
        factorSort=np.sort(factorX[i,])#np.sort 默认升序排列，nan在最后
        factorSortIdx=np.argsort(factorX[i,])                
        firstNanIdx=np.where(np.isnan(factorSort)==True)[0][0]
        factorSortIdx=factorSortIdx[:firstNanIdx]
        inGroupNum=int(round(len(factorSortIdx)/groupNum))#每组股票数
        for j in range(groupNum-1):
            factorGroup[i,j]=np.nanmean(factorY[i,factorSortIdx[inGroupNum*j:inGroupNum*(j+1)]])
        factorGroup[i,groupNum-1]=np.nanmean(factorY[i,factorSortIdx[inGroupNum*(groupNum-1):]])    
    for j in range(groupNum):
        pylab.plot_date(date,mvGroup[:,j],linestyle='-')
    label = [u'第1组',u'第2组',u'第3组',u'第4组',u'第5组']
    plt.legend(label)   
    return factorGroup
#分5组平均市值
mvGroup=group(Q,mv,groupNum)
plt.title(u'按Q排序分五组市值平均')
plt.show()  
#Q和市值的相关性
Q_mv_cor=np.zeros(len(date))
for i in range(len(date)):    
    nanIdx=np.union1d(np.where(np.isnan(Q[i,])==True)[0],np.where(np.isnan(mv[i,])==True)[0])    
    Q_mv_cor[i]=np.corrcoef(np.delete(Q[i,],nanIdx),np.delete(mv[i,],nanIdx))[0,1]
#分5组平均动量
momGroup=group(Q,stockRet,groupNum)
plt.title(u'按Q排序分五组动量平均')
plt.show()  
#Q和动量的相关性
Q_mom_cor=np.zeros(len(date))
for i in range(len(date)):    
    nanIdx=np.union1d(np.where(np.isnan(Q[i,])==True)[0],np.where(np.isnan(stockRet[i,])==True)[0])    
    Q_mom_cor[i]=np.corrcoef(np.delete(Q[i,],nanIdx),np.delete(stockRet[i,],nanIdx))[0,1]
#4.1行业虚拟变量
industryDummyDict={}
industryNum=27
for iIndustryDummyDict in range(1,industryNum):
    industryDummyDict[iIndustryDummyDict]=np.zeros(len(code))
    for iCode in range(len(code)):
        if industryDF[u'行业编号'][iCode]==iIndustryDummyDict:
            industryDummyDict[iIndustryDummyDict][iCode]=1
#4.2 Q对市值对数、动量（前20交易日涨跌幅）、行业虚拟变量回归

eps=np.zeros(Q.shape)
for i in range(Q.shape[0]):
    Y=Q[i,:]
    X=np.c_[np.log(mv[i,:]),stockRet[i,:]]
    for iIndustryDummyDict in range(1,industryNum):
        X=np.c_[X,industryDummyDict[iIndustryDummyDict]]
    nanIdx_Y=np.where(np.isnan(Y)==True)
    nanIdx_X=np.where((np.isnan(X[:,0])==True)|(np.isnan(X[:,1])==True))
    nanIdx=np.union1d(nanIdx_X[0],nanIdx_Y[0])
    #把nan值去掉后再代入np.linalg.lstsq  
    YdelNan=np.delete(Y, nanIdx)
    XdelNan=np.delete(X, nanIdx, axis=0)  
    l=np.linalg.lstsq(XdelNan,YdelNan)        
    eps[i,:]=Y-np.dot(X,l[0])
# 4.3剔除后的残差因子有效性检验
factorOriginal=eps
#4.3.1检验因子有效性
import singleFactor_RegValidity;reload(singleFactor_RegValidity)
[factorTvalue,factorRegValidity]=singleFactor_RegValidity.fun(stockRet,factorOriginal)
#4.3.2单因子分组回测
import singleFactor_GroupBacktest;reload(singleFactor_GroupBacktest)
groupPeriod=1;regressPeriod=1
backTestResult=singleFactor_GroupBacktest.fun(stockRet,factorOriginal,date,groupPeriod=groupPeriod,regressPeriod=regressPeriod)
    




