import datetime
import pathlib
from decimal import Decimal
from typing import List

import akshare as ak
import backtrader as bt
import pandas as pd

import akfix
import stocks


def get_datafile_name(stock_code):
    parent = pathlib.Path(__file__).parent
    return str(parent.joinpath("data/daily/"+stock_code+"_data.csv"))


def get_accu_datafile_name(stock_code):
    parent = pathlib.Path(__file__).parent
    return str(parent.joinpath("data/daily/"+stock_code+"_accu_data.csv"))


def force_load_stock_history(stock_code, source='sina'):
    filename = get_datafile_name(stock_code)
    if source == 'sina':
        history = ak.stock_zh_index_daily(symbol=stock_code)
    elif source == 'tx':
        history = ak.stock_zh_index_daily_tx(symbol=stock_code)
    history.to_csv(filename)
    return history


def force_load_stock_history_2(stock_code, start_date="19990101", end_date=None, adjust="qfq"):
    if end_date is None:
        end_date = str(datetime.date.today()).replace("-", "")
    filename = get_datafile_name(stock_code)
    history = akfix.stock_zh_a_hist(code=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    history.to_csv(filename)
    return history


def load_stock_history(stock_code, start=None, end=None, preview=False):
    filename = get_datafile_name(stock_code)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        history = force_load_stock_history_2(stock_code)
    return process_stock_history(history, start, end, preview)


def process_stock_history(df, start=None, end=None, preview=False):
    df['date_raw'] = df['date']
    df[['date']] = df[['date']].apply(pd.to_datetime)
    df.set_index(keys=['date'], inplace=True)
    result_df = None
    if start is None and end is None:
        result_df = df
    elif start is None and end is not None:
        result_df = df[:end]
    elif start is not None and end is None:
        result_df = df[start:]
    else:
        result_df = df.loc[start:end]
    if preview:
        last_date = result_df.tail(1).index.item()
        new_date = last_date + datetime.timedelta(days=1)
        result_df.loc[new_date] = result_df.loc[last_date]
    return result_df


def force_load_north():
    result = []
    for item in [('all', '北上'), ('sh', '沪股通'), ('sz', '深股通')]:
        history = force_load_north_single(item[0], item[1])
        result.append((item, history))
    return result


def load_north_single(type, start=None, end=None, preview=False):
    filename = get_datafile_name("north_%s" % type)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_north()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end, preview)


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

    return history


def force_load_north_2():
    force_load_north_2_single('sh', '沪股通')
    force_load_north_2_single('sz', '深股通')


def load_north_2_single(type, start=None, end=None, preview=False):
    filename = get_datafile_name("north_2_%s" % type)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_north_2()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end, preview)


def force_load_north_2_single(type, indicator):
    filename = get_datafile_name("north_2_%s" % type)

    new_history = ak.stock_hsgt_hist_em(symbol=indicator)

    new_history_renamed = pd.DataFrame(columns=['date', 'net_buy_vol', 'buy_vol', 'sell_vol', 'net_in'])
    new_history_renamed[['date', 'net_buy_vol', 'buy_vol', 'sell_vol', 'net_in']] = new_history[['日期', '当日成交净买额', '买入成交额', '卖出成交额', '当日资金流入']]

    new_history_renamed.sort_values(by=['date'], inplace=True)

    new_history_renamed.set_index(keys=[pd.Index(range(len(new_history_renamed)))], inplace=True)

    new_history_renamed.to_csv(filename)


def force_load_market_pe_history():
    for market in stocks.PEMarket:
        force_load_market_pe_history_single(market.code)


def force_load_market_pe_history_single(market):
    filename = get_datafile_name('market_pe_' + market)
    history = ak.stock_a_pe(symbol=market)
    history.to_csv(filename)
    return history


def load_market_pe_single(market, start=None, end=None, preview=False):
    filename = get_datafile_name('market_pe_' + market)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_market_pe_history()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end, preview)


def force_load_etf_accu_history(stock_code, start_date="19990101", end_date=None):
    if end_date is None:
        end_date = str(datetime.date.today()).replace("-", "")
    filename = get_accu_datafile_name(stock_code)
    loaded_history = ak.fund_etf_fund_info_em(fund=stock_code[2:], start_date=start_date, end_date=end_date)

    history = loaded_history.rename(columns={'单位净值': 'unit', '累计净值': 'accu', '日增长率': 'change_rate', '净值日期': 'date'})
    history.drop(columns=['申购状态', '赎回状态'], inplace=True)

    latest_unit = history.iloc[0]['unit']
    latest_accu = history.iloc[0]['accu']
    convert_rate = latest_unit / latest_accu
    history['accu_qfq'] = history['accu'] * convert_rate

    history.to_csv(filename)
    return history


def load_etf_accu_history(stock_code, start=None, end=None, preview=False):
    filename = get_accu_datafile_name(stock_code)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        history = force_load_etf_accu_history(stock_code)
    return process_stock_history(history, start, end, preview)


def load_stock_data(cerebro: bt.Cerebro, stocks: List[stocks.Stock], start: str, end: str, cnname: bool = True, preview=False):
    datas = []
    for stock in stocks:
        df = load_stock_history(stock.code, start, end, preview)
        data = bt.feeds.PandasData(dataname=df)
        if cnname:
            cerebro.adddata(data, name=stock.cnname)
        else:
            cerebro.adddata(data, name=stock.stockname)
        datas.append(data)
    return datas


def date_ahead(date: str, days: int):
    date_obj = datetime.datetime.fromisoformat(date)
    date_ahead = date_obj - datetime.timedelta(days=days)
    return str(date_ahead.date())


if __name__ == '__main__':
    for stock in stocks.Stock:
        history = force_load_stock_history_2(stock.code)
        print('%s %s loaded' % (stock.code, str(history.iloc[-1]['date'])))
        if not stock.is_index:
            accu_history = force_load_etf_accu_history(stock.code)
            print('%s %s accu loaded' % (stock.code, str(accu_history.iloc[0]['date'])))

    north_results = force_load_north()
    for north_result in north_results:
        north_item = north_result[0]
        history = north_result[1]
        print('%s %s loaded' % (north_item[1], str(history.iloc[-1]['date'])))

    force_load_north_2()
    print('north 2 loaded')

    force_load_market_pe_history()
    print('market PE loaded')
