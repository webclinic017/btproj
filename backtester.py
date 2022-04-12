import pathlib

import backtrader as bt
import quantstats
from backtrader.observers import BuySell, Broker, Trades, DataTrades

from loader import load_stock_data, date_ahead
from oberservers.RelativeValue import RelativeValue
from stocks import Stock
from strategies.strategy2 import Strategy2
from strategies.strategy4 import Strategy4
from strategies.strategy5 import Strategy5
from strategies.strategy6 import Strategy6
from strategies.strategydonatr import StrategyDonAtr
from strategies.strategynorth import StrategyNorth
from strategies.strategynorth2 import StrategyNorth2
from strategies.strategynorth3 import StrategyNorth3
from strategies.strategynorth4 import StrategyNorth4
from strategies.strategynorth5 import StrategyNorth5
from strategies.strategynorthsma import StrategyNorthWithSMA


def run(strategy, stocks, start=None, end=None, data_start=0, plot=True, report=True, printlog=True, benchmark=False, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    # Add a strategy
    cerebro.addstrategy(strategy_class, printlog=printlog, starttradedt=start, **kwargs)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    datas = load_stock_data(cerebro, stocks, date_ahead(start, data_start), end)

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
        cerebro.plot()


# start, end = '2014-06-18', None       #从开始到现在
# start, end = '2015-05-01', None       #2015股灾到现在
# start, end = '2015-05-01', '2019-01-01'       #2015股灾到2019爆发前夕
# start, end = '2014-06-18', '2019-01-01'       #从开始到2019爆发前夕
# start, end = '2019-01-01', '2020-12-31'       #此轮牛市
# start, end = '2020-07-01', '2021-03-31'
# start, end = '2018-01-01', '2021-08-13'
# start, end = '2017-12-01', None
# start, end = '2015-12-01', None
# start, end = '2020-10-01', None
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

run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2020-10-01', data_start=60, plot=False, printlog=False)
run(StrategyNorth, [Stock.CYB50ETF], start='2020-10-01', data_start=60, plot=False, printlog=False, market='sh')
run(StrategyNorth, [Stock.A50ETF], start='2020-10-01', data_start=60, plot=False, printlog=False, market='sh')
run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2020-10-01', data_start=60, plot=False, printlog=False, market='sh')
run(StrategyNorthWithSMA, [Stock.A50ETF], start='2020-10-01', data_start=60, plot=False, printlog=False, market='sh')

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
# start, end = '2017-10-01', '2023-10-01'
# run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start, end=end, data_start=365, plot=False, printlog=False)
# run(StrategyNorth, [Stock.CYB50ETF], start=start, end=end, data_start=365, plot=True, printlog=False, market='sh')
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start=start, end=end, data_start=365, plot=False, printlog=False, market='sh')