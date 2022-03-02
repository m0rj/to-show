from pydantic.typing import NoneType
import get_data as gd
import tinvest
import pandas as pd
from tinvest.schemas import CandleResolution as CR, Error, ErrorStreaming
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import talib
import time

pd.set_option('display.max_rows', None)

import logging
from telegram.ext import Updater, updater

import t_token

def send_text(text):
    logger = logging.getLogger(__name__)
    updater = Updater(t_token.UPDATER)
    updater.bot.send_message(t_token.CHAT_ID,text)

TOKEN = t_token.TOKEN

client = tinvest.SyncClient(TOKEN)

def df_resample(df, stock, start_time):
    start_time=start_time-start_time.utcoffset()
    #print(type(start_time))
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

df = gd.get_all_stocks(client)

for i in range(len(df)):
    print('Now: ',df['ticker'][i])
    stock_market_start= gd.get_tiker_start_date(df['ticker'][i])
    tmp_df = None
    time_btw_req = 0
    try:
        start_time = datetime.strptime(stock_market_start['stock_market_start'], '%Y-%m-%dT%H:%M:%S%z')
    except UnboundLocalError as e:
        pass
    except TypeError as e:
        pass
    while tmp_df is None:
        try:
            tmp_df = gd.get_ticker_candles(client,df['ticker'][i],datetime.now()-timedelta(days=28),datetime.now(),CR.min15)
            print('№:',i,'Now: ',df['ticker'][i],'Len:',len(tmp_df))
            tmp_df=df_resample(tmp_df, df['ticker'][i], start_time)

            if len(tmp_df)>14: 
                tmp_df['rsi'] = talib.RSI(tmp_df['c'], timeperiod=14)
                tmp_df['stk'], tmp_df['std'] = talib.STOCH(tmp_df['h'], tmp_df['l'], tmp_df['c'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
                print(len(tmp_df))
                print('RSI 4H',tmp_df['rsi'].iloc[-1])
                if tmp_df['stk'].iloc[-1]>tmp_df['std'].iloc[-1]:
                    if tmp_df['rsi'].iloc[-1]<40:
                        print(tmp_df['rsi'].iloc[-1])
                        print ('№:',i,'Now: ',df['ticker'][i],' RSI 15min: ', tmp_df['rsi'].iloc[-1])
                        res = '№:'+repr(i)+'Now: '+df['ticker'][i]+' RSI 15min: '+repr(tmp_df['rsi'].iloc[-1])
                        send_text(res)
        except tinvest.exceptions.TooManyRequestsError as e:
            time.sleep(1)
            time_btw_req=time_btw_req + 0.01
            print('tooManyRequests', time_btw_req)
            pass
        except NameError:
            pass

#send_text("sdfsdff")