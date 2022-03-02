import json
from urllib import request
#from matplotlib.pyplot import get_figlabels
import tinvest
from tinvest.exceptions import TinvestError
from tinvest.schemas import CandleResolution as CR, Error, ErrorStreaming
#from tinvest.schemas import MarketOrderRequest
from urllib.request import urlopen
from datetime import datetime
from datetime import timedelta
import requests
import pandas as pd
import time
import os.path

import t_token

TOKEN = t_token.TOKEN

client = tinvest.SyncClient(TOKEN)

def get_all_stocks(client):
    all_stocks = client.get_market_stocks()
    res = pd.DataFrame(vars(x) for x in all_stocks.payload.instruments)
    #res.to_csv('./data/all_stock_info')
    return res

def get_figi(tiker):
    figi = None
    while figi is None:
        try:
            figi = client.get_market_search_by_ticker(tiker).payload.instruments[0].figi
        except requests.exceptions.RequestException as e:
            print (e)
            pass
        except IndexError as e:
            print (e)
            break
    return figi

#print (get_figi('AAPL'))

def get_tiker_start_date(tiker):

    urlt = 'https://api-invest.tinkoff.ru/trading/stocks/get?ticker='+tiker

    json_url = urlopen(urlt)
    data = json.loads(json_url.read())
    #print(data['payload']['historyStartDate'])
    dtdata = None
    stock_market_start = None
    sessionClose = None
    try:
        dtdata = datetime.strptime(data['payload']['historyStartDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
        stock_market_start=data['payload']['symbol']['sessionOpen']
        sessionClose=data['payload']['symbol']['sessionClose']
    except Exception:
        print("Не тот формат")
    try:
        dtdata = datetime.strptime(data['payload']['historyStartDate'], '%Y-%m-%dT%H:%M:%Sz')
        stock_market_start=data['payload']['symbol']['sessionOpen']
        sessionClose=data['payload']['symbol']['sessionClose']
    except Exception:
        print("не тот формат")
    try:
        dtdata = datetime.strptime(data['payload']['historyStartDate'], '%Y-%m-%dT%H:%M:%SZ')
        stock_market_start=data['payload']['symbol']['sessionOpen']
        sessionClose=data['payload']['symbol']['sessionClose']
    except Exception:
        print("не тот формат")
    return {'dtdata':dtdata, 'stock_market_start':stock_market_start, 'sessionClose':sessionClose}

#mins: from mins to day
#hour: from 1 hour to 7 days
#days: from 1 day to 1 year
#month looong

def get_data_loop(client, tiker, _from, _to, CR):
    #Разобраться с датами часовыми поясами
    time_btw_req = 0.01
    _from=_from.replace(tzinfo=None)
    _to=_to.replace(tzinfo=None)
    figi = get_figi(tiker)
    dat1e = _from
    df = pd.DataFrame(columns=['c','figi','h','interval','l','o','time','v'])
    #print('INDEX NAME: ', df.index.name)
    if CR in (CR.min1, CR.min2, CR.min3, CR.min5, CR.min10, CR.min15, CR.min30): dchunk = 1
    if CR in CR.hour: dchunk = 7
    if CR in CR.day: dchunk = 365
    #print("Дней от начала до конца:" , int((_to-_from).days))
    for dcount in range(int((_to-_from).days)//dchunk):
        dat2e = dat1e+timedelta(days=dchunk,milliseconds=-1)
        resp = None
        while resp is None:
            try:
                resp = client.get_market_candles(figi,dat1e,dat2e,CR)
            except requests.exceptions.RequestException as e:
                print(e)
                pass
            except tinvest.exceptions.TooManyRequestsError as e:
                time.sleep(1)
                time_btw_req=time_btw_req + 0.01
                print('tooManyRequests', time_btw_req)
                pass
            except tinvest.BadRequestError as e:
                print(e)
                return df
        dat1e = dat1e+timedelta(days=dchunk)
        #print(dcount)
        res = pd.DataFrame(vars(x) for x in resp.payload.candles)
        df = df.append(res, ignore_index=True)
        time.sleep(time_btw_req)    
        dcount=+1
    return df

def get_ticker_candles(client, tiker, _from, _to, CR):
    figi = get_figi(tiker)
    if _from == 'START' and get_tiker_start_date(tiker) != None:
        _from = get_tiker_start_date(tiker)
        print(_from)
        print(type(_from))
    if _to == 'NOW':
        _to = datetime.now()
        #print(_to)
        #print (type(_to))
    df = get_data_loop(client, tiker, _from, _to, CR)
    #print('!!!!!!!!!!!!!!!!!!!!!!!!')
    #df.to_csv("./data/all_stocks/"+tiker+'_'+CR+".csv")
    return df

def download_all_stock(client,CR):
    df = pd.read_csv('./data/all_stock_info')
    #print (df[['figi','ticker']])
    for i in range(len(df)):
        if os.path.isfile("./data/all_stocks/"+df['ticker'][i]+'_'+CR+".csv"):
            print(df['ticker'][i],CR,'.csv Уже скачал !!')
        else:
            print('Качаю', df['ticker'][i], CR)
            get_ticker_candles(client,df['ticker'][i],'START','NOW',CR)

#download_all_stock(client,CR.min15)

print(get_all_stocks(client))

#print(get_tiker_start_date('AAPL'))
##print('!!!!!')
#print(get_ticker_candles(client,'AAPL','START','NOW',CR.min1))
#print(get_ticker_candles(client,'AAPL','START','NOW',CR.min15))
##print(get_ticker_candles(client,'MMM','START','NOW',CR.min15))
#print(res[['time','c','h','l','o','v','interval']])

