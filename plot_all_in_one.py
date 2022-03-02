from posix import listdir
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from datetime import date, datetime
from zigzag import *
import talib
import matplotlib.pyplot as plt
import os



def all_indi(df):
    window = 28 #сколько свечей берем

    df['rsi'] = talib.RSI(df['c'], timeperiod=14)
    df['stk'], df['std'] = talib.STOCH(df['h'], df['l'], df['c'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['c'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['mom'] = talib.MOM(df['c'], timeperiod=10)

    pivots = peak_valley_pivots(df['c'],0.10,-0.10)
    df['pivots']=pivots

    pivotdf = df[df['pivots']!=0].index
    #print("Колличество пивотов:", len(pivotdf))
    finnp_data = np.empty((len(pivotdf),window,window))
    nparr = np.empty((1,window,window))
    finnp_labels = np.empty((len(pivotdf),1))
    for i in range(len(pivotdf)):
        if i == 0 or i == len(pivotdf):
            continue
        #print(pivotdf[i]-(window-1))
        curwind = pivotdf[i]-(window-1)
        if curwind >=window: # проверяем что б от начала сета до пивотной точки были данные размером с окно
            res=df[['rsi','stk','std','macd','macdsignal','macdhist','mom','pivots']][pivotdf[i]-(window-1):pivotdf[i]+1]
            if res['pivots'].iloc[-1] == -1: 
                plt.plot(range(0,window),res['rsi'],'r-', alpha=0.005)
        i=i+1

    nparr = np.full((window,window),0)
    plt.ylim(0,100)

stock_list = os.listdir('./data/downloaded_stocks')
for i in stock_list:
    print('./data/downloaded_stocks/'+i)
    df = pd.read_csv('./data/downloaded_stocks/'+i)
    if len(df)>1000:
        all_indi(df)

plt.show()