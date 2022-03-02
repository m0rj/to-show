from datetime import timedelta
from datetime import datetime
from numpy.core.numeric import indices
from numpy.lib.arraysetops import isin
#from pandas._libs.tslibs import Hour
from pyecharts import Kline, EffectScatter, Overlap
from zigzag import *
import pandas as pd
import numpy
from pyecharts.option import color, effect
import talib
import get_data as gd


df = pd.read_csv('./data/AAPL15min.csv')
#print(df['time'][1])
#re=gd.get_tiker_start_date('AAPL')

def df_resample(df, stock, start_time):
    start_time=start_time-start_time.utcoffset()
    print(type(start_time))
    start_time = start_time.replace(microsecond=0, second=0, minute=0)
    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_time+'+00:00'
    #ori = datetime.strptime(re['stock_market_start'], '%Y-%m-%dT%H:%M:%S%z')
    df['time'] = pd.to_datetime(df['time'])
    resampled_df = df.resample('4H', on='time', origin=start_time).agg({
    'o': 'first',
    'h': 'max',
    'l': 'min',
    'c': 'last',
    'v': 'sum'
    })
    #print(resampled_df['v'][0:10])
    resampled_df = resampled_df.dropna()
    resampled_df = resampled_df.reset_index()
    return resampled_df

def get_pivots(df):
    pivots_df = peak_valley_pivots(df['c'],0.03,-0.03)
    df['pivots']=pivots_df

    candles_df = df[['o','c','l','h']]
    candles = candles_df.values.tolist()

    pivots_df = df[['pivots']]
    pivots=pivots_df.loc[(pivots_df['pivots'] == 1) | (pivots_df['pivots'] == -1)]

    pivots_x = pivots.index
    pivots_y = []

    #print(len(pivots_x))

    for i in range(len(pivots_x)):
        if df['pivots'][pivots_x[i]] == 1:
            #print(df['h'][pivots_x[i]])
            pivots_y.append(df['h'][pivots_x[i]])
        if df['pivots'][pivots_x[i]] == -1:
            pivots_y.append(df['h'][pivots_x[i]])
            #print(df['l'][pivots_x[i]])
    return  candles, pivots_x, pivots_y

def draw_graph(df, candles, pivots_x, pivots_y):
    kline = Kline("Apple")
    kline._width = 1300
    kline._height = 800
    kline.add("Apple", df.index, candles, is_datazoom_show=True,effect_period=0)
    kline.render()

    es=EffectScatter("Pivots")
    es._width = 1300
    es._height = 800
    es.add("effectScatter", pivots_x, pivots_y,symbol_size=6)
    es.render()

    overlap = Overlap()
    overlap.add(kline)
    overlap.add(es)
    overlap.render('h4.html')

df_h4 = df_resample(df,'AAPL', )

#print(df_h4)
#print(df)

candles, pivots_x, pivots_y = get_pivots(df_h4)
draw_graph(df_h4, candles, pivots_x, pivots_y)