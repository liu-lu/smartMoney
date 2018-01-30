# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 12:49:11 2018

@author: Zhang
"""
import feather
import pandas as pd
import numpy as np 
import math 
import os
import datetime

def findtimebound(filepath):
    filenamelist = os.listdir(filepath)
    starttime = []
    endtime = []
    count = 0
    for filename in filenamelist:
        try:
            path = os.path.join('%s%s' % (filepath,filename))
            df= feather.read_dataframe(path)
            thisstart = pd.to_datetime(df['date'][0])
            thisend = pd.to_datetime(df['date'][len(df)-1])
            if len(starttime) == 0:
                starttime.append(filename)
                starttime.append(thisstart)
            else:
                if starttime[1]>thisstart:
                    starttime[0] = filename
                    starttime[1] = thisstart
            if len(endtime) == 0:
                endtime.append(filename)
                endtime.append(thisend)
            else:
                if endtime[1]<thisend:
                    endtime[0] = filename
                    endtime[1] = thisend
            count = count+1
            print("\rrunning: {:.2f}%".format(count*100/len(filenamelist)),end="")
        except:
            print("error in generatetime: %s" %filename)
            count = count+1
            print("\rrunning: {:.2f}%".format(count*100/len(filenamelist)),end="")
            continue
    return [starttime, endtime]


def generatetimeindex(df):
    origindate = pd.to_datetime(df.date)
    length = len(origindate)
    timeindex = []
    for i in range(0,length-1):
        if origindate[i+1].month - origindate[i].month != 0:
            timeindex.append(origindate[i])
    return timeindex


def calculateQ(df,timeindex):
    # 1 calculation of factor Q
    # 1.1. original method
    #R = abs((df.close - df.preClose)/df.preClose)
    #df_vol = df['amount']/df['vwap']
    #S = R/df_vol.apply(math.sqrt)
    #df = df.drop(['open','low','high','preClose','close','preClose2','amount'], axis=1)
    #df['S'] = S
    #df['Vol'] = df_vol
    # 1.2. ACD method
    # from GF alpha 因子何处觅
    # ACD 收集派发指标
    df_vol = df['amount']/df['vwap']
    df = df.drop(['amount'],axis = 1)
    is_index = df.index[df.close > df.preClose]   
    temp = pd.DataFrame()
    temp['low'] = df.low[is_index]
    temp['preClose'] = df.preClose[is_index]
    minn = pd.DataFrame.min(temp,axis = 1)
    df['R'] = -1
    df.R[is_index] = pd.DataFrame.copy((df.close[is_index]-minn)/df.preClose[is_index])
    is_index = df.index[df.close < df.preClose]   
    temp = pd.DataFrame()
    temp['high'] = df.high[is_index]
    temp['preClose'] = df.preClose[is_index]
    maxx = pd.DataFrame.max(temp,axis = 1)
    df['R'][is_index] = pd.DataFrame.copy(abs(df.close[is_index]-maxx)/df.preClose[is_index])
    df['R'][df.preClose==df.close] = 0
    df['S'] = df.R/df_vol.apply(math.sqrt)
    df = df.drop(['open','low','high','preClose','close','preClose2'], axis=1)
    df['Vol'] = df_vol
    # 1.3 寻找每个月最后一个交易日
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df['pos'] = range(0,len(df))
    Q = pd.Series(-1.0,timeindex)                                #Q是名称-时间-Q的列表
    for i in range(0,len(timeindex)):    
        try:
            position = df.pos[timeindex[i]]
            thisdata = df.iloc[position-2400+1:position+1]
            if sum(np.isnan(thisdata['Vol']))/2400 >= 0.40:
                Q[i] = -2
                continue
            data_sorted= thisdata.sort_values('S',ascending=False)
            vol = data_sorted['Vol'].cumsum()
            data_sorted['isSmart'] = vol < max(vol) * 0.2
            smartIndex = data_sorted.index[data_sorted.isSmart == True]
            sumsmart = np.nansum(data_sorted['Vol'][smartIndex])
            sumall = np.nansum(data_sorted['Vol'])
            vwapsmart = data_sorted['vwap'][smartIndex]*data_sorted['Vol'][smartIndex]/sumsmart
            vwapall = data_sorted['vwap']*data_sorted['Vol']/sumall
            Q[i] = np.nansum(vwapsmart)/np.nansum(vwapall)
        except:
            #print("\n calculating; something is wrong in %s%d" %(filename,i))
            continue
    return Q


def readandrun(filepath,Group):
    numberofstocks = {'SH':1290,'SZ':1979,'S':3269}
    filenamelist = os.listdir(filepath)
    timeindexdf = feather.read_dataframe('H:/1m data/1/SH600000.feather') # find this with findtimebound
    timeindex = generatetimeindex(timeindexdf)
    count = 0
    Q = pd.DataFrame()
    for filename in filenamelist:
        if Group in filename:
            try: 
                path = os.path.join('%s%s' % (filepath, filename))
                df = feather.read_dataframe(path)
                tempQ = calculateQ(df,timeindex)
                Q[filename] = tempQ
                count = count+1
                print("\rrunning: {:.2f}%".format(count*100/numberofstocks[Group]),end="")
            except:
                print("\n readandrun; something is wrong in %s" %filename)
                count = count+1
                print("\rrunning: {:.2f}%".format(count*100/numberofstocks[Group]),end="")
                continue
    return Q


               
def main(Group):
    filepath = 'H:/1m data/1/'
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    Q = readandrun(filepath,Group)
    Savefile = Group + '_Q.csv'
    Q.to_csv(Savefile)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
   

#timebound = findtimebound(filepath)   # result: SH600000.feather
main('SH')



















