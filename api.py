#!/usr/bin/python
# -*- encoding: utf-8 -*-

__author__ = 'Olschewski, Jan'


# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
import yfinance as yf
from pandas_finance import Equity

### API
from api_key import BINANCE_API_SECRET, BINANCE_API_KEY

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "2h": 120,"4h": 240, "1d": 1440}
batch_size = 750

binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    if source == "binance":
        new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    return old, new

def get_all_binance(symbol, kline_size, save = True):
    filename = 'data_with_indicators/%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source = "binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: data_df = data
    data_df.set_index('Datetime', inplace=True)
    if save:
        data_df.to_csv(f'{filename}', sep=";")
    print('All caught up..!')
    return data_df



def get_stock_data(symbol, timeframe="1h", daily=False, days=365):
    period_map = {"1h": "730d", "15m": "60d","5m": "60d"}
    df = yf.Ticker(symbol)
    df = df.history(period=period_map[timeframe], interval=timeframe)
    filename = 'data_with_indicators/%s-%s-data.csv' % (symbol, timeframe)
    #df.set_index('Datetime', inplace=True)
    df.to_csv(f'{filename}', sep=";")
    return df
