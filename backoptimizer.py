import json

import backtrader as bt

from stocks import Stock
from loader import load_stock_data, date_ahead
from strategies.strategy2 import Strategy2
from strategies.strategy4 import Strategy4
from strategies.strategy5 import Strategy5
from strategies.strategynorth import StrategyNorth


# start, end = '2014-06-18', None       #从开始到现在
# start, end = '2015-05-01', None       #2015股灾到现在
# start, end = '2015-05-01', '2019-01-01'       #2015股灾到2019爆发前夕
# start, end = '2014-06-18', '2019-01-01'       #从开始到2019爆发前夕
# start, end = '2019-01-01', '2020-12-31'       #此轮牛市
# start, end = '2020-07-01', '2021-03-31'
# start, end = '2018-01-01', None
from strategies.strategynorthsma import StrategyNorthWithSMA

durations = [
    # ('2014-06-18', None),
    # ('2015-05-01', None),
    # ('2014-06-18', '2019-01-01'),
    # ('2014-06-18', '2019-01-01'),
    # ('2019-01-01', '2020-12-31'),
    ('2015-12-01', None),
    # ('2018-01-22', '2020-06-30'),
    ('2016-07-22', '2020-07-07'),
    # ('2016-07-22', '2019-01-30'),
    # ('2015-05-01', '2019-01-01'),
    # (None, None)
]

for duration in durations:
    start, end = duration

    cerebro = bt.Cerebro()

    # cerebro.optstrategy(Strategy1, maperiod=[5, 10, 20, 60], minchgpct=range(0, 4, 1), printlog=False)
    # cerebro.optstrategy(Strategy2, buyperiod=[10, 20, 60], sellperiod=[5, 10, 20], minchgpct=range(0, 4, 1),
    #                     printlog=False)
    # cerebro.optstrategy(Strategy4, buyperiod=[10, 20, 60], sellperiod=[5, 10, 20], minchgpct=range(0, 4, 1),
    #                     printlog=False, starttradedt=start)
    cerebro.optstrategy(Strategy5, buyperiod=[10, 20, 30, 60], sellperiod=[5, 10, 20], minchgpct=range(0, 4, 1),
                        shouldbuypct=[0.2, 0.5, 0.7], printlog=False, starttradedt=start)
    # cerebro.optstrategy(StrategyNorth, period=[60, 120, 250, 500], highpercent=[0.6, 0.7, 0.8, 0.9],
    #                     lowpercent=[0.1, 0.2, 0.3, 0.4], maxdrawback=[0.02, 0.05, 0.1, 0.2],
    #                     printlog=False)
    # cerebro.optstrategy(StrategyNorth, period=[250, 500], highpercent=[0.8, 0.9],
    #                     lowpercent=[0.1, 0.2], maxdrawback=[0.02, 0.05, 0.1, 0.2],
    #                     offset=[0, 1, 5, 10, 20], printlog=False)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    load_stock_data(
        cerebro,
        [Stock.HS300, Stock.CYB50, Stock.ZZ500],
        # [Stock.HS300ETF, Stock.CYB50ETF],
        # [Stock.CYB50ETF],
        # [Stock.CYB50],
        date_ahead(start, 90),
        end
    )

    print('Optimizing %s, %s' % duration)

    initial_cash = 1000000.0
    cerebro.broker.setcash(initial_cash)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    optimized_runs = cerebro.run(maxcpus=1)

    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            trades = strategy.analyzers.trades.get_analysis()
            drawdown = strategy.analyzers.drawdown.get_analysis()
            net_total = trades['pnl']['net']['total']
            win_rate = trades['won']['total'] / (trades['won']['total'] + trades['lost']['total'])
            max_drawdown = drawdown['max']['drawdown']
            pd_rate = net_total / max_drawdown / initial_cash * 100
            sharpe_ratio = sharpe['sharperatio']
            final_results_list.append((json.dumps(strategy.params.__dict__),
                                       net_total,
                                       win_rate,
                                       max_drawdown,
                                       pd_rate,
                                       sharpe_ratio,
                                       ))

    sort_by_sharpe = sorted(final_results_list, key=lambda x: x[1],
                            reverse=True)
    for line in sort_by_sharpe[:10]:
        print('Param: %s, PNL Net %f, Win Rate %.2f, Max Drawdown %.2f, Profit Drawdown Rate %.2f, Sharp Ratio %f' % line)
