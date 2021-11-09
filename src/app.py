import backtrader as bt
from flask import Flask, stream_with_context

import stocks
from loader import load_stock_data, force_load_stock_history, force_load_north, force_load_market_pe_history
from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategynorth import StrategyNorth

app = Flask(__name__)


@app.route("/daily")
def daily_strategy():
    logs = []
    logs = logs + run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start='2020-10-01')
    logs.append('')
    logs = logs + run(StrategyNorth, [Stock.CYB50ETF], start='2020-10-01')
    return "<br/>".join(logs)


@app.route("/load")
def load():
    def generate():
        for stock in stocks.Stock:
            force_load_stock_history(stock.code)
            yield '%s loaded<br/>' % stock.code

        force_load_north()
        yield 'north loaded<br/>'

        force_load_market_pe_history()
        yield 'market PE loaded<br/>'

    return app.response_class(stream_with_context(generate()))


def run(strategy, stocks, start=None, end=None):
    cerebro = bt.Cerebro()

    strategy_class = strategy

    cerebro.addstrategy(strategy_class, printlog=False)

    load_stock_data(cerebro, stocks, start, end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    logs = [str(strategy_class.__name__), 'Starting Portfolio Value: %.3f' % cerebro.broker.getvalue()]

    cerebro.run()
    logs = logs + cerebro.runstrats[0][0].logs

    logs.append('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    return logs
