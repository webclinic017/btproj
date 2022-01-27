import datetime
import pathlib
from typing import List

import akshare as ak
import backtrader as bt
import pandas as pd

import stocks


def get_datafile_name(stock_code):
    parent = pathlib.Path(__file__).parent
    return str(parent.joinpath("data/daily/"+stock_code+"_data.csv"))


def force_load_stock_history(stock_code):
    filename = get_datafile_name(stock_code)
    history = ak.stock_zh_index_daily(symbol=stock_code)
    history.to_csv(filename)
    return history


def load_stock_history(stock_code, start=None, end=None):
    filename = get_datafile_name(stock_code)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        history = force_load_stock_history(stock_code)
    return process_stock_history(history, start, end)


def process_stock_history(df, start=None, end=None):
    df['date_raw'] = df['date']
    df[['date']] = df[['date']].apply(pd.to_datetime)
    df.set_index(keys=['date'], inplace=True)
    if start is None and end is None:
        return df
    elif start is None and end is not None:
        return df[:end]
    elif start is not None and end is None:
        return df[start:]
    else:
        return df.loc[start:end]


def force_load_north():
    force_load_north_single('all', '北上')
    force_load_north_single('sh', '沪股通')
    force_load_north_single('sz', '深股通')


def load_north_single(type, start=None, end=None):
    filename = get_datafile_name("north_%s" % type)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_north()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end)


def force_load_north_single(type, indicator):
    filename = get_datafile_name("north_%s" % type)
    try:
        existing_history = pd.read_csv(filename)
    except FileNotFoundError:
        existing_history = None

    new_history = ak.stock_hsgt_north_net_flow_in_em(symbol=indicator)

    if existing_history is None:
        history = new_history
    else:
        history = existing_history.append(new_history).drop_duplicates(subset=['date'], keep='last')
        history = history.drop(columns=['Unnamed: 0'])
        history.set_index(keys=[pd.Index(range(len(history)))], inplace=True)

    history.to_csv(filename)


def force_load_market_pe_history():
    for market in stocks.PEMarket:
        force_load_market_pe_history_single(market.code)


def force_load_market_pe_history_single(market):
    filename = get_datafile_name('market_pe_' + market)
    history = ak.stock_a_pe(symbol=market)
    history.to_csv(filename)
    return history


def load_market_pe_single(market, start=None, end=None):
    filename = get_datafile_name('market_pe_' + market)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_market_pe_history()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end)


def load_stock_data(cerebro: bt.Cerebro, stocks: List[stocks.Stock], start: str, end: str):
    for stock in stocks:
        df = load_stock_history(stock.code, start, end)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name=stock.stockname)


def date_ahead(date: str, days: int):
    date_obj = datetime.datetime.fromisoformat(date)
    date_ahead = date_obj - datetime.timedelta(days=days)
    return str(date_ahead.date())

if __name__ == '__main__':
    for stock in stocks.Stock:
        force_load_stock_history(stock.code)
        print('%s loaded' % stock.code)

    force_load_north()
    print('north loaded')

    force_load_market_pe_history()
    print('market PE loaded')
