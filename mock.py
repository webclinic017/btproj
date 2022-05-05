import pathlib
from datetime import datetime, timedelta

import backtrader as bt
import pandas as pd
import random

import quantstats
from backtrader.observers import Broker, BuySell, Trades, DataTrades

from loader import process_stock_history
from oberservers.RelativeValue import RelativeValue
from strategies.strategy4 import Strategy4


def gen_data(start_date: datetime, count: int, change_pct_limit=10):
    df = pd.DataFrame()
    time_delta = timedelta(days=1)
    date = start_date
    open = 1000
    for i in range(count):
        change_pct = random.gauss(0.0002, 4)
        print(change_pct)
        if change_pct > change_pct_limit / 100:
            change_pct = change_pct_limit
        elif change_pct < -change_pct_limit / 100:
            change_pct = -change_pct_limit
        close = open * (100 + change_pct) / 100
        if change_pct > 0:
            high = close
            low = open
        else:
            high = open
            low = close

        row = pd.Series(
            data={'date': date.strftime('%Y-%m-%d'), 'open': open, 'high': high, 'low': low, 'close': close},
            name=i + 1)
        df = df.append(row)

        date = date + time_delta
        open = close

    return df


def load_stock_data(cerebro: bt.Cerebro, dfs):
    datas = []
    for i in range(len(dfs)):
        df = process_stock_history(dfs[i])
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name="S%d" % i)
        datas.append(data)
    return datas


def run_mock(strategy, dfs, start=None, plot=True, report=True, printlog=True, benchmark=False, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    # Add a strategy
    cerebro.addstrategy(strategy_class, printlog=printlog, starttradedt=start, **kwargs)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    datas = load_stock_data(cerebro, dfs)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.addobserver(Broker)
    cerebro.addobservermulti(BuySell, bardist=0)
    cerebro.addobservermulti(RelativeValue, starttradedt=start)
    if len(datas) == 1:
        cerebro.addobserver(Trades)
    else:
        cerebro.addobserver(DataTrades)

    if benchmark:
        for data in datas:
            cerebro.addobserver(bt.observers.Benchmark, data=data, timeframe=bt.TimeFrame.Days)

    print(str(strategy_class.__name__))
    print('Starting Portfolio Value: %.3f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    if report:
        portfolio_stats = results[0].analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        folder = 'report-mock'
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

        filename = '%s_%s-%d' % (strategy_class.__name__, start, len(dfs))
        for k, v in kwargs.items():
            filename += '_%s=%s' % (k, v)

        quantstats.reports.html(
            returns,
            output='%s/%s.html' % (folder, filename),
            title=strategy_class.__name__)

    if plot:
        cerebro.plot(volume=False)


if __name__ == '__main__':
    count = 1500
    df = gen_data(datetime(2000, 1, 1), count)
    print(df.head(count))
    # dfs = []
    # for i in range(3):
    #     dfs.append(gen_data(datetime(2000, 1, 1), count))
    #
    # run_mock(Strategy4, dfs, start='2000-06-01', plot=True, printlog=True, mode=1, rsi=((30, 5), (25, 5), (24, 5)))
