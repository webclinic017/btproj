import datetime
import pathlib

import backtrader as bt
import pandas as pd
import quantstats
from backtrader.observers import BuySell, Broker, Trades, DataTrades

from loader import load_stock_data, date_ahead
from oberservers.RelativeValue import RelativeValue
from stocks import Stock
from strategies.strategy0 import Strategy0
from strategies.strategy2 import Strategy2
from strategies.strategy2SMA import Strategy2SMA
from strategies.strategy4 import Strategy4
from strategies.strategy4ATR import Strategy4ATR
from strategies.strategy4phase import Strategy4Phase
from strategies.strategy5 import Strategy5
from strategies.strategy6 import Strategy6
from strategies.strategySMA import StrategySMA
from strategies.strategySMAMulti import StrategySMAMulti
from strategies.strategydisplay import StrategyDisplay
from strategies.strategydonatr import StrategyDonAtr
from strategies.strategynorth import StrategyNorth
from strategies.strategynorth2 import StrategyNorth2
from strategies.strategynorth3 import StrategyNorth3
from strategies.strategynorth4 import StrategyNorth4
from strategies.strategynorth5 import StrategyNorth5
from strategies.strategynorthsma import StrategyNorthWithSMA

pd.options.mode.chained_assignment = None


def run(strategy, stocks, start=None, end=None, data_start=0, plot=True, report=True, printlog=True, benchmark=False,
        preview=False, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    # Add a strategy
    cerebro.addstrategy(strategy_class, printlog=printlog, starttradedt=start, **kwargs)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    datas = load_stock_data(cerebro, stocks, date_ahead(start, data_start), end, cnname=False, preview=preview)

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
            output='%s/%s.html' % (folder, filename),
            title=strategy_class.__name__)

    if plot:
        cerebro.plot(style='candle', barup='red', bardown='green', barupfill=False, bardownfill=False, start=datetime.datetime.strptime(start, "%Y-%m-%d"))
        # cerebro.plot(start=datetime.datetime.strptime(start, "%Y-%m-%d"))


def run_data_plot(stock, start=None, end=None, data_start=0):
    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(StrategyDisplay)

    load_stock_data(cerebro, [stock], date_ahead(start, data_start), end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.run()

    cerebro.plot(style='candle', start=datetime.datetime.strptime(start, "%Y-%m-%d"))
    # cerebro.plot(style='candle', barup='red', bardown='green', barupfill=False, bardownfill=False,
    #              start=datetime.datetime.strptime(start, "%Y-%m-%d"))


# start, end = '2014-06-18', None       #从开始到现在
# start, end = '2015-05-01', None       #2015股灾到现在
# start, end = '2015-05-01', '2019-01-01'       #2015股灾到2019爆发前夕
# start, end = '2014-06-18', '2019-01-01'       #从开始到2019爆发前夕
# start, end = '2019-01-01', '2020-12-31'       #此轮牛市
# start, end = '2020-07-01', '2021-03-31'
# start, end = '2018-01-01', '2021-08-13'
# start, end = '2017-12-01', None
# start, end = '2015-12-01', None
# start, end = '2021-08-25', None
# start, end = '2020-01-01', None   #科创板开始到现在
# start, end = '2021-02-10', None
# start, end = '2018-01-22', '2020-06-30'   #HS300EFT 一次下探恢复
# start, end = '2016-07-22', '2020-07-07'   #CYB50EFT 一次下探恢复
# start, end = '2016-07-22', '2018-10-16' #CYB50ETF 最高到最低
# start, end = '2018-10-16', None   #CYB50ETF 最低点到现在
# start, end = None, None   #CYB50EFT 开始到现在

# stocks = [Stock.HS300, Stock.CYB50]
# stocks = [Stock.HS300]
# stocks = [Stock.CYB50]
# stocks = [Stock.HS300ETF, Stock.CYB50ETF]
# stocks = [Stock.HS300ETF]
# stocks = [Stock.CYB50ETF]
# stocks = [Stock.KC50]
# stocks = [Stock.HS300, Stock.KC50]

run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, preview=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
run(Strategy4Phase, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.ZZ1000ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, preview=False, mode=2,
    rsi=((30, 5), (25, 5), (24, 5), (24, 5)), buyperiod=18, sellperiod=22, minchgpct=0, shouldbuypct=0.3, halfrate=50, backdays=3)
run(Strategy4Phase, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, preview=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2015-01-01', data_start=60, plot=True, printlog=False, preview=False,
#     mode=2, rsi=((30, 5), (25, 5), (24, 5)), buyperiod=15, sellperiod=21, minchgpct=3, shouldbuypct=-1)
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.KC50ETF], start='2021-01-01', end='2022-01-01', data_start=60, plot=False, printlog=True, mode=2, rsi=((30, 5), (25, 5), (24, 5), (20, 5)))
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-08-25', data_start=60, plot=False, printlog=True, mode=1)
# run(StrategyNorth, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorth, [Stock.A50ETF], start='2021-08-25', data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=3, halfrate=10)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=3, modehalf=False)
# run(StrategyNorthWithSMA, [Stock.A50ETF], start='2021-08-25', data_start=60, plot=False, printlog=False, market='sh', mode=3)
# run(StrategyNorthWithSMA, [Stock.A50ETF], start='2021-08-25', data_start=60, plot=False, printlog=False, market='sh', mode=3,
#     periodbull=250, highpercentbull=0.8, lowpercentbull=0.4, maxdrawbackbull=0.05, periodbear=120, highpercentbear=0.9, lowpercentbear=0.2, maxdrawbackbear=0.1, smaperiod=10)

# run(StrategyBias, [Stock.HS300ETF], start='2017-08-25', data_start=365, plot=True, printlog=False)

# run(Strategy2SMA, [Stock.CYB50], start='2016-08-25', data_start=120, plot=True, printlog=False, smaperiodfast=10, smaperiodslow1=30, smaperiodslow2=30, mode=2, atrratio=1)
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2016-08-25', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2016-08-25', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)), buyperiod=21, sellperiod=16, minchgpct=0, shouldbuypct=0)
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-10-01', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)), sellperiod=20, minchgpct=0, shouldbuypct=0.7)
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-10-01', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)), buyperiod=18, sellperiod=23, minchgpct=2, shouldbuypct=0)
#
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-10-01', data_start=60, plot=False, printlog=False, mode=1, buyperiod=20, sellperiod=20, minchgpct=0, shouldbuypct=0.7)
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-10-01', data_start=60, plot=False, printlog=False, mode=1, buyperiod=18, sellperiod=23, minchgpct=2, shouldbuypct=0)

# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-08-25', data_start=60, plot=True, printlog=True, market='sh', mode=3)

# run(Strategy2SMA, [Stock.CYB50], start='2015-08-25', data_start=120, plot=True, printlog=False, smaperiodfast=10, smaperiodslow1=30, smaperiodslow2=30, mode=3, atrratio=1)
# run(Strategy2SMA, [Stock.CYB50], start='2015-08-25', data_start=120, plot=True, printlog=False, smaperiodfast=10, smaperiodslow1=30, smaperiodslow2=30, mode=3, atrratio=2)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2021-08-25', data_start=60, plot=False, printlog=True, market='sh', mode=1)
# run(StrategyNorthWithSMA, [Stock.A50ETF], start='2021-08-25', data_start=60, plot=False, printlog=False, market='sh', mode=1)
# run(StrategySMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, mode=1)
# run(StrategySMAMulti, [Stock.CYB50ETF, Stock.ZZ500ETF, Stock.HS300ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, rsi=((74, 25, 5), (74, 24, 5), (74, 30, 5)))
# run(StrategySMA, [Stock.CYB50], start='2014-08-25', data_start=60, plot=True, printlog=False, mode=1)

# run(StrategyNorth5, [Stock.CYB50ETF], start='2020-03-20', data_start=365, plot=True, printlog=False, market='sh')

# run(StrategyNorth, [Stock.CYB50], start='2022-01-01', plot=True, printlog=False, market='sh')
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2022-01-01', data_start=60, plot=True, printlog=False)
# run(Strategy5, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2020-12-01', data_start=60, plot=False, printlog=False)

# run(StrategyNorth, [Stock.CYB50ETF], start='2018-01-01', end="2018-12-31", data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorth, [Stock.CYB50ETF], start='2018-01-01', end="2018-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=250, highpercent=0.9, lowpercent=0.1, maxdrawback=0.02)
#
# run(StrategyNorth, [Stock.CYB50ETF], start='2019-01-01', end="2019-12-31", data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorth, [Stock.CYB50ETF], start='2019-01-01', end="2019-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=60, highpercent=0.8, lowpercent=0.4, maxdrawback=0.02)
# run(StrategyNorth, [Stock.CYB50ETF], start='2019-01-01', end="2019-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=60, highpercent=0.8, lowpercent=0.4, maxdrawback=0.05)
#
# run(StrategyNorth, [Stock.CYB50ETF], start='2020-01-01', end="2020-12-31", data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorth, [Stock.CYB50ETF], start='2020-01-01', end="2020-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=120, highpercent=0.6, lowpercent=0.3, maxdrawback=0.05)
# run(StrategyNorth, [Stock.CYB50ETF], start='2020-01-01', end="2020-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=60, highpercent=0.8, lowpercent=0.4, maxdrawback=0.05)
#
# run(StrategyNorth, [Stock.CYB50ETF], start='2021-01-01', end="2021-12-31", data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorth, [Stock.CYB50ETF], start='2021-01-01', end="2021-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=120, highpercent=0.6, lowpercent=0.1, maxdrawback=0.05)
# run(StrategyNorth, [Stock.CYB50ETF], start='2021-01-01', end="2021-12-31", data_start=60, plot=False, printlog=False, market='sh',
#     period=500, highpercent=0.7, lowpercent=0.4, maxdrawback=0.05)


# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-01-01', end="2022-12-31", data_start=60, plot=True, printlog=True)
# run(StrategyNorth, [Stock.CYB50ETF], start='2022-01-01', end="2022-12-31", plot=True, printlog=False, market='sh')
# run(Strategy4, [Stock.ZGHLWETF, Stock.ZQETF, Stock.QSETF, Stock.HJETF, Stock.XNYCETF, Stock.YHETF, Stock.XPETF, Stock.JGETF],
#     start='2020-06-01', end="2020-12-31", buyperiod=10, sellperiod=10, shouldbuypct=0, minchgpct = 0, data_start=60, plot=True, printlog=False)

# run(StrategyDonAtr, [Stock.HS300ETF], start='2017-06-01', end="2021-12-31", data_start=365, plot=True, printlog=False)
# start, end = '2016-10-01', '2023-10-01'
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start, end=end, data_start=365, plot=False, printlog=False)
# run(StrategyNorth, [Stock.CYB50ETF], start=start, end=end, data_start=365, plot=True, printlog=False, market='sh')
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start=start, end=end, data_start=365, plot=False, printlog=False, market='sh')

# run(Strategy0, [Stock.CYB50], start='2014-10-01', data_start=60, plot=False, printlog=True, rsihigh=82, rsilow=0, period=5)
# run(Strategy0, [Stock.HS300], start='2002-06-01', data_start=60, plot=False, printlog=True, rsihigh=83, rsilow=0, period=5)
# run(Strategy0, [Stock.ZZ500], start='2014-01-01', data_start=60, plot=False, printlog=True, rsihigh=100, rsilow=24)

# run(Strategy0, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=True, rsihigh=80, rsilow=25, period=5)
# run(Strategy0, [Stock.HS300ETF], start='2014-01-01', data_start=60, plot=False, printlog=True, rsihigh=83, rsilow=30, period=5)
# run(Strategy0, [Stock.ZZ500ETF], start='2014-01-01', data_start=60, plot=False, printlog=True, rsihigh=80, rsilow=24, period=5)


# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=1)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2019-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=2)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=3)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=4)

# run(StrategyNorthWithSMA, [Stock.A50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh', mode=2)
# run(StrategyNorthWithSMA, [Stock.A50ETF], start='2017-01-01', data_start=60, plot=False, printlog=True, market='sh', mode=3)

# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2019-01-01', data_start=60, plot=False, printlog=False, mode=1, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2019-01-01', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, mode=3, rsi=((30, 5), (25, 5), (24, 5)))

# run(StrategyNorth, [Stock.CYB50ETF], start='2017-01-01', data_start=60, plot=False, printlog=False, market='sh')

# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2014-10-01', data_start=60, plot=False, printlog=False, mode=1, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2014-10-01', data_start=60, plot=False, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2014-10-01', data_start=60, plot=False, printlog=False, mode=3, rsi=((30, 5), (25, 5), (24, 5)))

# run(StrategyNorth, [Stock.CYB50ETF], start='2019-01-01', end="2022-01-01", data_start=60, plot=False, printlog=False, market='sh')
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2021-07-01', end="2022-01-01", data_start=60, plot=True, printlog=False, market='sh', mode=3)

# run(StrategySMA, [Stock.CYB50ETF], start='2017-01-01', end="2022-05-01", data_start=60, plot=True, printlog=False, rsihigh=74, mode=1)
# run(StrategySMA, [Stock.CYB50ETF], start='2017-01-01', end="2022-05-01", data_start=60, plot=True, printlog=False, rsihigh=74, mode=2)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2017-01-01', end="2022-05-01", data_start=60, plot=True, printlog=False, market='sh', mode=3)
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2021-07-01', end="2022-05-01", data_start=60, plot=True, printlog=False, mode=2, rsi=((30, 5), (25, 5), (24, 5)))


# run(StrategySMA, [Stock.HS300ETF], start='2017-01-01', end="2022-05-01", data_start=60, plot=False, printlog=False, rsihigh=76, smaperiod=30, daystobuy=7, daystosell=3)
# run(StrategySMA, [Stock.HS300ETF], start='2019-01-01', end="2022-05-01", data_start=60, plot=True, printlog=False, rsihigh=85, rsilow=30, smaperiod=30, daystobuy=7, daystosell=3)
# run(StrategySMA, [Stock.HS300ETF], start='2017-01-01', end="2022-01-01", data_start=60, plot=True, printlog=False, rsihigh=85, rsilow=30, smaperiod=40, daystobuy=5, daystosell=3)
# run(StrategySMA, [Stock.HS300ETF], start='2017-01-01', end="2022-01-01", data_start=60, plot=True, printlog=False, rsihigh=85, rsilow=30, smaperiod=20, daystobuy=6, daystosell=5, mode=1)
# run(StrategySMA, [Stock.HS300ETF], start='2017-01-01', end="2022-05-01", data_start=60, plot=True, printlog=False, rsihigh=85, rsilow=30, smaperiod=20, daystobuy=6, daystosell=5, mode=2)

# run_data_plot(Stock.ZZ500ETF, start='2020-01-01')