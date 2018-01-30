def fun(stockRet,factorOriginal,sigLevel=0.05):
    import numpy as np
    import scipy.stats
    import math        
    import factor_Standardized;#reload(factor_Standardized)
    factor=factor_Standardized.fun(factorOriginal)
    [mStockRet,nStockRet]=stockRet.shape
    regCoef=np.zeros(mStockRet)*np.nan
    for i in range(1,mStockRet):
        Y=stockRet[i,:]
        X=np.c_[factor[i-1,:],np.ones(nStockRet)]#按列合并	
        nanIdx_Y=np.where(np.isnan(Y)==True)
        nanIdx_X=np.where(np.isnan(X[:,0])==True)
        nanIdx=np.union1d(nanIdx_X[0],nanIdx_Y[0])
        #把nan值去掉后再代入np.linalg.lstsq  
        Y=np.delete(Y, nanIdx, axis=None)
        X=np.delete(X, nanIdx, axis=0)  
        if len(X)>21:
            regCoef[i]=np.linalg.lstsq(X,Y)[0][0]
    
    df=sum(1-np.isnan(regCoef))-1#自由度 
    if df==0:
        factorTvalue=np.nanmean(regCoef)
        factorRegValidity=np.sign(factorTvalue)
    else:        
        factorTvalue=math.sqrt(df)*np.nanmean(regCoef)/np.nanstd(regCoef,ddof=1);
        if factorTvalue>scipy.stats.t.ppf(1-sigLevel/2,df):
            factorRegValidity=1
        elif factorTvalue<scipy.stats.t.ppf(sigLevel/2,df):
            factorRegValidity=-1
        else:
            factorRegValidity=0
    
    return factorTvalue,factorRegValidity
    
    import matplotlib.pyplot as plt
    plt.plot(regCoef)



