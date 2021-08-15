import backtrader as bt
import quantstats

from strategy2 import Strategy2
from stocks import load_stock_data
from stocks import Stock

from strategy1 import Strategy1
from strategynorth import StrategyNorth

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    strategy_class = StrategyNorth

    # Add a strategy
    cerebro.addstrategy(strategy_class)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    # start, end = '2014-06-18', None       #从开始到现在
    # start, end = '2015-05-01', None       #2015股灾到现在
    # start, end = '2015-05-01', '2019-01-01'       #2015股灾到2019爆发前夕
    # start, end = '2014-06-18', '2019-01-01'       #从开始到2019爆发前夕
    # start, end = '2019-01-01', '2020-12-31'       #此轮牛市
    # start, end = '2020-07-01', '2021-03-31'
    # start, end = '2018-01-01', '2021-08-13'
    # start, end = '2017-12-01', None
    # start, end = '2015-12-01', None
    # start, end = '2020-12-01', None
    # start, end = '2018-01-22', '2020-06-30'   #HS300EFT 一次下探恢复
    # start, end = '2016-07-22', '2020-07-07'   #CYB50EFT 一次下探恢复
    start, end = '2016-07-22', '2018-10-16' #CYB50ETF 最高到最低
    # start, end = '2018-10-16', None   #CYB50ETF 最低点到现在

    # stocks = [Stock.HS300, Stock.CYB50]
    # stocks = [Stock.HS300ETF, Stock.CYB50ETF]
    # stocks = [Stock.HS300ETF]
    stocks = [Stock.CYB50ETF]
    # stocks = [Stock.HS300, Stock.KC50]

    load_stock_data(cerebro, stocks, start, end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00002)

    print('Starting Portfolio Value: %.3f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    portfolio_stats = results[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    quantstats.reports.html(
        returns,
        output='../report/%s_%s-%s_%s.html' % (strategy_class.__name__, start, end, "-".join(map(lambda s: s.stockname, stocks))),
        title=strategy_class.__name__)

    cerebro.plot()
