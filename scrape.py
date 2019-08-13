import os
import pickle
import json
import numpy as np
import pandas as pd
import datetime as dt
import sys
import time

from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_available(top, apikey):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start':'1',
      'limit':'2000'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': '{0}'.format(apikey),
    }
    session = requests.Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)['data']
        coins = [i['slug'] for i in data][:top]
        tickers = [i['symbol'] for i in data][:top]
        return coins, tickers
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def init_folders():
    for d in ['/tables']:
        if not os.path.exists(os.getcwd()+d):
            os.makedirs(os.getcwd()+d)

def init_scraping(coins, tickers):
    url = 'https://coinmarketcap.com/currencies/{0}/historical-data/?start=20130428&end=20221013'
    keys = ['date', 'open', 'high', 'low', 'close', 'volume', 'capitalization']
    for name, ticker in zip(coins, tickers):
        if not os.path.isfile('tables/{0}.csv'.format(ticker)) or os.stat('tables/{0}.csv'.format(ticker)).st_size < 100:
            try:
                print("Loading...{0}".format(ticker))
                print(url.format(name))
                data = requests.get(url.format(name))
                soup = BeautifulSoup(data._content.decode('utf-8', 'ignore'))
                historical = soup.find(id="historical-data")
                rows = []
                for tr in historical.find_all('tr'):
                    columns = tr.find_all('td')
                    if columns:
                        vals = [td.text for td in columns]
                        rows.append(dict(zip(keys, vals)))
                
                # Format into dataframe
                df = pd.DataFrame.from_dict(rows)
                df['date'] = pd.to_datetime(df.date, format='%b %d, %Y')
                df.index = df['date'].map(lambda x: "{0}-{1}-{2}".format(x.year, x.month, x.day))
                df['capitalization'] = df['capitalization'].map(lambda x: '0' if x=="-" else x)
                df['capitalization'] = df['capitalization'].map(lambda x: float(x.replace(',' , '')))
                df['volume'] = df['volume'].map(lambda x: '0' if x=="-" else x)
                df['volume'] = df['volume'].map(lambda x: float(x.replace(',' , '')))
                df['open'] = df['open'].map(lambda x: float(x))
                df['low'] =  df['low'].map(lambda x: float(x))
                df['high'] = df['high'].map(lambda x: float(x))
                df['close'] = df['close'].map(lambda x: float(x))
                del df['date']
                df.to_csv('tables/{0}.csv'.format(ticker))

                time.sleep(1)
            except Exception as e:
                print(e)
                print("Restarting...")
                time.sleep(30)
                init_scraping(coins, tickers)
        else:
            print("Already downloaded {0}".format(ticker))

def init_dominance():
    data = []
    for filename in os.listdir('tables'):
        coin = filename.strip('.csv')
        if filename.endswith(".csv"): 
            try:
                TKR = pd.read_csv(os.path.join('tables', filename), index_col=0)
                TKR.index = pd.to_datetime(TKR.index)
                TKR = TKR.sort_index()
                TKR = TKR['capitalization'].to_frame(coin)
                data.append(TKR)
            except Exception as e: 
                print(e)
    df = pd.concat(data, axis=1)
    df['ALT'] = df[[i for i in df.columns if i != 'BTC']].sum(1)
    df['BTCD'] = df['BTC']/(df['BTC']+df['ALT'])
    df = df[['BTC', 'ALT', 'BTCD']]
    df.to_csv('BTCD.csv')
    print("Finished!")

if __name__ == "__main__":
    if sys.argv[1].startswith('top'):
        top = int(sys.argv[1].split('=')[1])
    if sys.argv[2].startswith('apikey'):
        apikey = str(sys.argv[2].split('=')[1])

    init_folders()
    coins, tickers = get_available(top, apikey)
    init_scraping(coins, tickers)
    init_dominance()
