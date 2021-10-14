import backtrader as bt
import quantstats

from loader import load_stock_data
from stocks import Stock
from strategies.strategy2 import Strategy2
from strategies.strategy4 import Strategy4
from strategies.strategynorth import StrategyNorth
from strategies.strategynorthsma import StrategyNorthWithSMA


def run(strategy, stocks, start=None, end=None, plot=True, report=True, printlog=True):
    cerebro = bt.Cerebro()

    strategy_class = strategy

    # Add a strategy
    cerebro.addstrategy(strategy_class, printlog=printlog)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    load_stock_data(cerebro, stocks, start, end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    print('Starting Portfolio Value: %.3f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    if report:
        portfolio_stats = results[0].analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        quantstats.reports.html(
            returns,
            output='../report/%s_%s-%s_%s.html' % (
            strategy_class.__name__, start, end, "-".join(map(lambda s: s.stockname, stocks))),
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

# run(Strategy2, stocks, start, end)
# run(StrategyNorth, stocks, start, end)


# run(Strategy2, [Stock.HS300, Stock.CYB50], start='2015-01-01')
# run(Strategy2, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2015-01-01')
# run(Strategy2, [Stock.HS300, Stock.CYB50], start='2015-05-01', end='2019-01-01')
# run(Strategy2, [Stock.HS300, Stock.CYB50], start='2016-08-31')
# run(Strategy2, [Stock.HS300, Stock.CYB50], start='2018-08-31')
# run(StrategyNorth, [Stock.CYB50], start='2015-01-01')
# run(StrategyNorthWithSMA, [Stock.CYB50], start='2015-01-01')
# run(StrategyNorth, [Stock.HS300], start='2015-01-01')
# run(StrategyNorth, [Stock.ZZ500], start='2015-01-01')
run(Strategy2, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2020-10-01', plot=False, printlog=False)
run(Strategy2, [Stock.HS300ETF, Stock.CYB50ETF], start='2020-10-01', plot=False, printlog=False)
run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2020-10-01', plot=False, printlog=False)
run(StrategyNorth, [Stock.CYB50ETF], start='2020-10-01', plot=False, printlog=False)
# run(StrategyNorthWithSMA, [Stock.CYB50ETF], start='2020-10-01', plot=False, printlog=False)
# run(StrategyNorth, [Stock.CYB50], start='2016-07-22', end='2020-07-07')
# run(StrategyNorthWithSMA, [Stock.CYB50], start='2016-01-22', end='2018-07-07')
# run(Strategy2, [Stock.HS300, Stock.CYB50], start='2015-05-01', end='2019-01-01', plot=False, printlog=False)
# run(Strategy4, [Stock.HS300, Stock.CYB50], start='2015-05-01', end='2019-01-01', plot=False, printlog=False)
# run(Strategy2, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2015-05-01', end='2019-01-01', plot=False, printlog=False)
# run(Strategy4, [Stock.HS300, Stock.CYB50, Stock.ZZ500], start='2015-05-01', end='2019-01-01', plot=False, printlog=False)