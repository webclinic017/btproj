import backtrader as bt
from backtrader_plotting import Bokeh
from flask import Flask, stream_with_context

import pathlib
import stocks
from loader import load_stock_data, force_load_stock_history, force_load_north, get_datafile_name
from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategynorth import StrategyNorth

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
    Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF
    <a href="daily/1">Log</a> <a href="plot/1">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorth for CYB50ETF
    <a href="daily/2">Log</a> <a href="plot/2">Plot</a>
    </h1>
    <br/><br/>
    <h1>
    StrategyNorth for A50ETF
    <a href="daily/3">Log</a> <a href="plot/3">Plot</a>
    </h1>
    <br/><br/>
    <a href="load"><h1>Load Latest Data</h1></a>
    <br/><br/>
    <a href="datalist"><h1>Show Data List</h1></a>
    </body>
    </html>"""


@app.route("/daily")
def daily_strategy():
    start_date = '2020-10-01'
    logs = []
    logs = logs + run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date)
    logs.append('')
    logs = logs + run(StrategyNorth, [Stock.CYB50ETF], start=start_date)
    logs.append('')
    logs = logs + run(StrategyNorth, [Stock.A50ETF], start=start_date)
    return '<a href="/">Back</a><br/><br/>' + "<br/>".join(logs)


@app.route("/daily/<int:id>")
def daily_strategy_logs(id):
    start_date = '2020-10-01'
    logs = []
    if id == 1:
        logs = run(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, printLog=True)
    elif id == 2:
        logs = run(StrategyNorth, [Stock.CYB50ETF], start=start_date, printLog=True)
    elif id == 3:
        logs = run(StrategyNorth, [Stock.A50ETF], start=start_date, printLog=True)
    return '<a href="/">Back</a><br/><br/>' + "<br/>".join(logs)


@app.route("/plot/<int:id>")
def daily_strategy_plot(id):
    start_date = '2020-10-01'
    html = 'Invalid strategy'
    if id == 1:
        html = run_plot(Strategy4, [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF], start=start_date, printLog=True)
    elif id == 2:
        html = run_plot(StrategyNorth, [Stock.CYB50ETF], start=start_date, printLog=True)
    elif id == 3:
        html = run_plot(StrategyNorth, [Stock.A50ETF], start=start_date, printLog=True)
    return html


@app.route("/load")
def load():
    def generate():
        yield '<a href="/">Back</a><br/><br/>'
        for stock in stocks.Stock:
            force_load_stock_history(stock.code)
            yield '%s loaded<br/>' % stock.code

        force_load_north()
        yield 'north loaded<br/>'

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


def run(strategy, stocks, start=None, end=None, printLog=False):
    cerebro = bt.Cerebro()

    strategy_class = strategy

    cerebro.addstrategy(strategy_class, printlog=printLog)

    load_stock_data(cerebro, stocks, start, end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    logs = [str(strategy_class.__name__), 'Starting Portfolio Value: %.3f' % cerebro.broker.getvalue()]

    cerebro.run()
    logs = logs + cerebro.runstrats[0][0].logs

    logs.append('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    return logs


def run_plot(strategy, stocks, start=None, end=None, printLog=False):
    cerebro = bt.Cerebro()

    strategy_class = strategy

    cerebro.addstrategy(strategy_class, printlog=printLog)

    load_stock_data(cerebro, stocks, start, end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.run()

    filename = 'plot/app.html'

    b = Bokeh(style='bar', plot_mode='single', filename=filename, show=False, output_mode='save')
    cerebro.plot(b)

    return pathlib.Path(filename).read_text()
