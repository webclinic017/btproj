import datetime
import pathlib

import backtrader as bt
import pandas as pd
import quantstats
from backtrader.observers import BuySell, Broker, Trades, DataTrades

from loader import load_stock_data, date_ahead
from oberservers.RelativeValue import RelativeValue
from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategySMA import StrategySMA
from strategies.strategynorthsma import StrategyNorthWithSMA

pd.options.mode.chained_assignment = None


def run(strategy, stocks, start=None, end=None, data_start=0, plot=True, report=True, printlog=True, benchmark=False,
        preview=False, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    # Add a strategy
    cerebro.addstrategy(strategy_class, printlog=printlog, starttradedt=start, **kwargs)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    datas, _ = load_stock_data(cerebro, stocks, date_ahead(start, data_start), end, cnname=False, preview=preview)

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

        folder = 'report'
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

        filename = '%s_%s-%s_%s' % (strategy_class.__name__, start, end, "-".join(map(lambda s: s.stockname, stocks)))
        for k, v in kwargs.items():
            filename += '_%s=%s' % (k, v)

        quantstats.reports.html(
            returns,
            output="file",
            download_filename='%s/%s.html' % (folder, filename),
            title=strategy_class.__name__)

    if plot:
        cerebro.plot(style='candle', barup='red', bardown='green', barupfill=False, bardownfill=False, start=datetime.datetime.strptime(start, "%Y-%m-%d"))
        # cerebro.plot(start=datetime.datetime.strptime(start, "%Y-%m-%d"))


start = '2021-08-25'
run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start, data_start=60, plot=False, printlog=False, preview=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start, data_start=60, plot=False, printlog=False, preview=True, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
run(StrategyNorthWithSMA, [Stock.CYB50ETF], start=start, data_start=60, plot=False, printlog=False)
run(StrategyNorthWithSMA, [Stock.A50ETF], start=start, data_start=60, plot=False, printlog=False,
    periodbull=250, highpercentbull=0.8, lowpercentbull=0.4, maxdrawbackbull=0.05,
    periodbear=120, highpercentbear=0.9, lowpercentbear=0.2, maxdrawbackbear=0.1,
    smaperiod=10, modehalf=False)
run(StrategySMA, [Stock.CYB50ETF], start=start, data_start=60, plot=False, printlog=False, mode=1)
