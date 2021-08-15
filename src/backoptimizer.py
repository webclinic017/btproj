import json

import backtrader as bt

from stocks import Stock
from stocks import load_stock_data
from strategy1 import Strategy1
from strategy2 import Strategy2
from strategynorth import StrategyNorth

if __name__ == '__main__':
    # start, end = '2014-06-18', None       #从开始到现在
    # start, end = '2015-05-01', None       #2015股灾到现在
    # start, end = '2015-05-01', '2019-01-01'       #2015股灾到2019爆发前夕
    # start, end = '2014-06-18', '2019-01-01'       #从开始到2019爆发前夕
    # start, end = '2019-01-01', '2020-12-31'       #此轮牛市
    # start, end = '2020-07-01', '2021-03-31'
    # start, end = '2018-01-01', None

    durations = [
        # ('2014-06-18', None),
        # ('2015-05-01', None),
        # ('2014-06-18', '2019-01-01'),
        # ('2014-06-18', '2019-01-01'),
        # ('2019-01-01', '2020-12-31'),
        # ('2015-12-01', None),
        ('2018-01-22', '2020-06-30'),
        ('2016-07-22', '2020-07-07')
    ]

    for duration in durations:
        start, end = duration

        cerebro = bt.Cerebro()

        # cerebro.optstrategy(Strategy1, maperiod=[5, 10, 20, 60], minchgpct=range(0, 4, 1), printlog=False)
        # cerebro.optstrategy(Strategy2, buyperiod=[10, 20, 60], sellperiod=[5, 10, 20], minchgpct=range(0, 4, 1),
        #                     printlog=False)
        cerebro.optstrategy(StrategyNorth, period=[0, 20, 60, 120, 250, 500], highpercent=[0.6, 0.7, 0.8, 0.9],
                            lowpercent=[0.1, 0.2, 0.3, 0.4], printlog=False)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

        load_stock_data(
            cerebro,
            # [Stock.HS300ETF, Stock.CYB50ETF],
            [Stock.CYB50ETF],
            start,
            end
        )

        print('Optimizing %s, %s' % duration)

        initial_cash = 1000000.0
        cerebro.broker.setcash(initial_cash)
        cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
        cerebro.broker.setcommission(commission=0.00002)

        optimized_runs = cerebro.run(maxcpus=1)

        final_results_list = []
        for run in optimized_runs:
            for strategy in run:
                sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
                returns = strategy.analyzers.returns.get_analysis()
                final_results_list.append((json.dumps(strategy.params.__dict__),
                                           returns['rtot'],
                                           sharpe['sharperatio'],
                                           ))

        sort_by_sharpe = sorted(final_results_list, key=lambda x: x[1],
                                reverse=True)
        for line in sort_by_sharpe[:5]:
            print('Param: %s, Final Value %f, Sharp Ratio %f' % line)
