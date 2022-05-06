import backtrader as bt
from backtrader.observers import Broker, BuySell, Trades, DataTrades
from backtrader_plotting import Bokeh
from flask import Flask, stream_with_context

import pathlib
import stocks
from loader import load_stock_data, force_load_stock_history, force_load_north, get_datafile_name, date_ahead
from oberservers.RelativeValue import RelativeValue
from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategy5 import Strategy5
from strategies.strategynorth import StrategyNorth
from strategies.strategynorthsma import StrategyNorthWithSMA

app = Flask(__name__)


@app.route("/")
def home():
    return """<html>
    <head>
    <title>Daily Strategy</title>
    </head>
    <body>
    <a href="daily"><h1>Daily Strategy</h1></a>
    <br/><br/>
    <h1>
    Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 2
    <a href="log/1">Log</a> <a href="plot/1">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 1
    <a href="log/4">Log</a> <a href="plot/4">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorth for CYB50ETF
    <a href="log/2">Log</a> <a href="plot/2">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorth for A50ETF
    <a href="log/3">Log</a> <a href="plot/3">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorthWithSMA for CYB50ETF
    <a href="log/5">Log</a> <a href="plot/5">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorthWithSMA for A50ETF
    <a href="log/6">Log</a> <a href="plot/6">Plot</a>
    </h1>
    <br/><br/>
    <a href="load"><h1>Load Latest Data</h1></a>
    <br/><br/>
    <a href="datalist"><h1>Show Data List</h1></a>
    </body>
    </html>"""


@app.route("/daily", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/daily/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/daily/<string:start_date>/<string:start_trade_date>')
def daily_strategy(start_date, start_trade_date):
    logs = []
    logs = logs + run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
    logs.append('')
    logs = logs + run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, mode=1)
    logs.append('')
    logs = logs + run(StrategyNorth, [Stock.CYB50ETF], start=start_date)
    logs.append('')
    logs = logs + run(StrategyNorth, [Stock.A50ETF], start=start_date)
    logs.append('')
    logs = logs + run(StrategyNorthWithSMA, [Stock.CYB50ETF], data_start=60, start=start_date)
    logs.append('')
    logs = logs + run(StrategyNorthWithSMA, [Stock.A50ETF], data_start=60, start=start_date)
    return '<a href="/">Back</a><br/><br/>' + "<br/>".join(logs)


@app.route("/log/<int:id>", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/log/<int:id>/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/log/<int:id>/<string:start_date>/<string:start_trade_date>')
def daily_strategy_logs(id, start_date, start_trade_date):
    logs = []
    if id == 1:
        logs = run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, printLog=True, mode=2, rsi=((30, 5), (25, 5), (24, 5)))
    elif id == 2:
        logs = run(StrategyNorth, [Stock.CYB50ETF], start=start_date, starttradedt=start_trade_date, printLog=True)
    elif id == 3:
        logs = run(StrategyNorth, [Stock.A50ETF], start=start_date, starttradedt=start_trade_date, printLog=True)
    if id == 4:
        logs = run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, printLog=True, mode=1)
    elif id == 5:
        logs = run(StrategyNorthWithSMA, [Stock.CYB50ETF], start=start_date, starttradedt=start_trade_date, data_start=60, printLog=True)
    elif id == 6:
        logs = run(StrategyNorthWithSMA, [Stock.A50ETF], start=start_date, starttradedt=start_trade_date, data_start=60, printLog=True)
    return '<a href="/">Back</a><br/><br/>' + "<br/>".join(logs)


@app.route("/plot/<int:id>", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/plot/<int:id>/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/plot/<int:id>/<string:start_date>/<string:start_trade_date>')
def daily_strategy_plot(id, start_date, start_trade_date):
    html = 'Invalid strategy'
    if id == 1:
        html = run_plot(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, printLog=False, mode=2, rsi="((30, 5), (25, 5), (24, 5))")
    elif id == 2:
        html = run_plot(StrategyNorth, [Stock.CYB50ETF], start=start_date, starttradedt=start_trade_date, printLog=False)
    elif id == 3:
        html = run_plot(StrategyNorth, [Stock.A50ETF], start=start_date, starttradedt=start_trade_date, printLog=False)
    if id == 4:
        html = run_plot(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, data_start=60, starttradedt=start_trade_date, printLog=False, mode=1)
    elif id == 5:
        html = run_plot(StrategyNorthWithSMA, [Stock.CYB50ETF], start=start_date, starttradedt=start_trade_date, data_start=60, printLog=False)
    elif id == 6:
        html = run_plot(StrategyNorthWithSMA, [Stock.A50ETF], start=start_date, starttradedt=start_trade_date, data_start=60, printLog=False)
    return html


@app.route("/load")
def load():
    def generate():
        yield '<a href="/">Back</a><br/><br/>'
        for stock in stocks.Stock:
            history = force_load_stock_history(stock.code)
            yield '%s %s loaded<br/>' % (stock.code, str(history.iloc[-1]['date']))

        north_results = force_load_north()
        for north_result in north_results:
            north_item = north_result[0]
            history = north_result[1]
            yield '%s %s loaded<br/>' % (north_item[1], str(history.iloc[-1]['date']))

    return app.response_class(stream_with_context(generate()))


@app.route("/datalist")
def datalist():
    def generate():
        yield '<a href="/">Back</a><br/><br/>'
        for stock in stocks.Stock:
            yield '<a href="data/%s"><h1>%s</h1></a>' % (stock.code, stock.stockname)
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_all', 'North All')
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_sh', 'North Shanghai')
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_sz', 'North Shenzhen')

    return app.response_class(stream_with_context(generate()))


@app.route("/data/<stock_code>", defaults={'rows': 30})
@app.route('/data/<stock_code>/<int:rows>')
def data(stock_code, rows):
    def generate():
        lines = pathlib.Path(get_datafile_name(stock_code)).read_text().split("\n")
        lines = [lines[0]] + lines[-rows:][::-1]
        yield '<html>'
        yield '<style>'
        yield 'td {text-align: center;}'
        yield '</style>'
        yield '<body>'
        yield '<table border="1" cellspacing="0">'
        for line in lines:
            if len(line) > 0:
                yield "<tr>"
                for item in line.split(","):
                    yield '<td>'
                    yield item
                    yield "</td>"
                yield "</tr>"
        yield "</table>"
        yield "</body></html>"
    return app.response_class(stream_with_context(generate()))


def run(strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    if starttradedt is None:
        starttradedt = start

    cerebro.addstrategy(strategy_class, printlog=printLog, starttradedt=starttradedt, **kwargs)

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

    logs = [str(strategy_class.__name__), 'Starting Portfolio Value: %.3f' % cerebro.broker.getvalue()]

    cerebro.run()
    logs = logs + cerebro.runstrats[0][0].logs

    logs.append('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    return logs


def run_plot(strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False, **kwargs):
    cerebro = bt.Cerebro()

    strategy_class = strategy

    if starttradedt is None:
        starttradedt = start

    cerebro.addstrategy(strategy_class, printlog=printLog, starttradedt=starttradedt, **kwargs)

    load_stock_data(cerebro, stocks, date_ahead(start, data_start), end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.addobservermulti(RelativeValue, starttradedt=starttradedt)

    cerebro.run()

    folder = 'plot'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    filename = folder + '/app.html'

    b = Bokeh(style='bar', plot_mode='single', filename=filename, show=False, output_mode='save')
    cerebro.plot(b)

    return pathlib.Path(filename).read_text()
