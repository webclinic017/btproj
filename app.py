import datetime
import pathlib

import backtrader as bt
from backtrader.observers import Broker, BuySell, Trades, DataTrades
from backtrader_plotting import Bokeh
from flask import Flask, stream_with_context, request

import stocks
from loader import load_stock_data, force_load_stock_history, force_load_north, get_datafile_name, date_ahead
from oberservers.RelativeValue import RelativeValue
from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategySMA import StrategySMA
from strategies.strategydisplay import StrategyDisplay
from strategies.strategynorth import StrategyNorth
from strategies.strategynorthsma import StrategyNorthWithSMA

app = Flask(__name__)

strategies = [
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 2 New Args",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 60,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5))"},
        "core": True
    },
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 2",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 60,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5))", "buyperiod": 20, "sellperiod": 20, "minchgpct": 0, "shouldbuypct": 0.7},
        "core": False
    },
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 1",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 60,
        "args": {"mode": 1},
        "core": False
    },
    {
        "label": "StrategyNorth for CYB50ETF",
        "class": StrategyNorth,
        "stocks": [Stock.CYB50ETF],
        "data_start": 0,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorth for A50ETF",
        "class": StrategyNorth,
        "stocks": [Stock.A50ETF],
        "data_start": 0,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorthWithSMA for CYB50ETF",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.CYB50ETF],
        "data_start": 60,
        "args": {},
        "core": True
    },
    {
        "label": "StrategyNorthWithSMA for A50ETF",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.A50ETF],
        "data_start": 60,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorthWithSMA for A50ETF New Args",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.A50ETF],
        "data_start": 60,
        "args": {"periodbull": 250, "highpercentbull": 0.8, "lowpercentbull": 0.4, "maxdrawbackbull": 0.05,
                 "periodbear": 120, "highpercentbear": 0.9, "lowpercentbear": 0.2, "maxdrawbackbear": 0.1,
                 "smaperiod": 10, "modehalf": False},
        "core": True
    },
    {
        "label": "StrategySMA for CYB50ETF",
        "class": StrategySMA,
        "stocks": [Stock.CYB50ETF],
        "data_start": 60,
        "args": {"mode": 1},
        "core": False
    }
]


@app.route("/")
def home():
    strategy_contents = ""
    for i in range(len(strategies)):
        strategy = strategies[i]
        strategy_contents += """<div class="item">%s <a class="sublink" href="log/%d">Log</a> <a class="sublink" href="plot/%d">Plot</a></div>""" % (strategy["label"], i, i)

    content = """
<html>
<head>
<title>Daily Strategy</title>
<style>
.item {
  font-size: 30px;
  margin: 25px 0px;
}
.sublink {
  margin: 0px 10px;
}
</style>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
</head>
<body>
<div class="item">
    Daily Strategy
    <a class="sublink" href="daily?coreonly=False">All</a>
    <a class="sublink" href="daily?coreonly=True">Core Only</a>
</div>
%s
<div class="item">
    Load Latest Data 
    <a class="sublink" href="load?source=sina&coreonly=False">Sina All</a>
    <a class="sublink" href="load?source=sina&coreonly=True">Sina Core Only</a>
    <a class="sublink" href="load?source=tx&coreonly=False">Tencent All</a>
    <a class="sublink" href="load?source=tx&coreonly=True">Tencent Core Only</a>
</div>
<div class="item">
    <a href="datalist">Show Data List</a>
</div>
</body>
</html>
    """ % (strategy_contents)
    return content


@app.route("/daily", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/daily/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/daily/<string:start_date>/<string:start_trade_date>')
def daily_strategy(start_date, start_trade_date):
    coreonly = request.args.get('coreonly', default="False")
    logs = []
    for strategy in strategies:
        if coreonly != 'True' or strategy["core"]:
            logs.append(strategy["label"])
            logs = logs + run(strategy["class"], strategy["stocks"], start=start_date, data_start=strategy["data_start"],
                              starttradedt=start_trade_date, **strategy["args"])
            logs.append('')
    logs = list(map(lambda line: decorate_line(line), logs))

    content = """
<html>
<head>
<title>Daily Strategy</title>
<style>
</style>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
</head>
<body>
%s
</body>
</html>""" % '<a href="/">Back</a><br/><br/>' + "<br/>".join(logs)
    return content


@app.route("/log/<int:id>", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/log/<int:id>/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/log/<int:id>/<string:start_date>/<string:start_trade_date>')
def daily_strategy_logs(id, start_date, start_trade_date):
    strategy = strategies[id]
    logs = [strategy["label"]]
    logs = logs + run(strategy["class"], strategy["stocks"], start=start_date, data_start=strategy["data_start"],
                      starttradedt=start_trade_date, printLog=True, **strategy["args"])
    logs = list(map(lambda line: decorate_line(line), logs))

    content = """
<html>
<head>
<title>Daily Strategy</title>
<style>
</style>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
</head>
<body>
%s
</body>
</html>""" % ('<a href="/">Back</a><br/><br/>' + "<br/>".join(logs))
    return content


@app.route("/plot/<int:id>", defaults={'start_date': '2021-08-25', 'start_trade_date': None})
@app.route('/plot/<int:id>/<string:start_date>', defaults={'start_trade_date': None})
@app.route('/plot/<int:id>/<string:start_date>/<string:start_trade_date>')
def daily_strategy_plot(id, start_date, start_trade_date):
    strategy = strategies[id]
    html = run_plot(strategy["class"], strategy["stocks"], start=start_date, data_start=strategy["data_start"],
                    starttradedt=start_trade_date, printLog=False, **strategy["args"])
    return html


@app.route("/load")
def load():
    source = request.args.get('source', default="sina")
    coreonly = request.args.get('coreonly', default="False")
    def generate():
        yield """
<html>
<head>
<title>Daily Strategy</title>
<style>
</style>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
</head>
<body>"""
        yield '<div><a href="/">Back</a></div>'
        yield '<div><table>'
        for stock in stocks.Stock:
            if coreonly != 'True' or stock.core:
                history = force_load_stock_history(stock.code, source)
                yield '<tr><td>%s %s</td><td>%s</td><td>loaded</td></tr>' % (stock.code, stock.cnname, str(history.iloc[-1]['date']))

        north_results = force_load_north()
        for north_result in north_results:
            north_item = north_result[0]
            history = north_result[1]
            yield '<tr><td>%s</td><td>%s</td><td>loaded</td></tr>' % (north_item[1], str(history.iloc[-1]['date']))

        yield '</table></div>'
        yield '<div>Finished</div>'
        yield """</body></html>"""

    return app.response_class(stream_with_context(generate()))


@app.route("/datalist")
def datalist():
    def generate():
        yield """
<html>
<head>
<title>Daily Strategy</title>
<style>
</style>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
</head>
<body>"""
        yield '<a href="/">Back</a><br/><br/>'
        for stock in stocks.Stock:
            yield '<h1><a href="data/%s">%s</a> <a href="dataplot/%s">Plot</a></h1>' % (
                stock.code, stock.cnname, stock.code)
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_all', 'North All')
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_sh', 'North Shanghai')
        yield '<a href="data/%s"><h1>%s</h1></a>' % ('north_sz', 'North Shenzhen')
        yield """</body></html>"""

    return app.response_class(stream_with_context(generate()))


@app.route("/data/<stock_code>", defaults={'rows': 30})
@app.route('/data/<stock_code>/<int:rows>')
def data(stock_code, rows):
    stock = get_stock(stock_code)

    def generate():
        lines = pathlib.Path(get_datafile_name(stock_code)).read_text().split("\n")
        lines = [lines[0]] + lines[-rows:][::-1]
        yield """
<html>
<head>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="apple-touch-icon-precomposed" href="/static/favicon.ico">
<style>
td {text-align: right;}
</style>
</head>
<body>"""
        if stock is not None:
            yield '<p>' + stock.cnname + '</p>'
        yield '<p>' + stock_code + '</p>'
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


@app.route("/dataplot/<stock_code>", defaults={'start_date': None, 'end_date': None})
@app.route('/dataplot/<stock_code>/<string:start_date>', defaults={'end_date': None})
@app.route('/dataplot/<stock_code>/<string:start_date>/<string:end_date>')
def dataplot(stock_code, start_date, end_date):
    if start_date is None:
        today = datetime.date.today()
        start_date = str(today - datetime.timedelta(days=365))
    stock = get_stock(stock_code)
    html = run_data_plot([stock], start=start_date, end=end_date)
    return html


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


def run_data_plot(stocks, start=None, end=None, data_start=0):
    cerebro = bt.Cerebro()

    cerebro.addstrategy(StrategyDisplay)

    load_stock_data(cerebro, stocks, date_ahead(start, data_start), end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.run()

    folder = 'plot'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    filename = folder + '/app.html'

    b = Bokeh(style='bar', plot_mode='single', filename=filename, show=False, output_mode='save')
    cerebro.plot(b)

    return pathlib.Path(filename).read_text()


def get_stock(stock_code):
    for stock in stocks.Stock:
        if stock_code == stock.code:
            return stock
    return None


def decorate_line(line: str):
    if line.find('Last Order') > -1:
        if line.rfind(line[:10]) == 0:
            return """<span style="color:gray">%s</span>""" % line
    if line.find(' for ') > -1:
        return """<span style="color:blue">%s</span>""" % line
    if line.find('BUY CREATE') > -1 or line.find('BUY EXECUTED') > -1:
        return """<span style="color:green">%s</span>""" % line
    if line.find('OPERATION PROFIT') > -1 or line.find('SELL CREATE') > -1 or line.find('SELL EXECUTED') > -1:
        return """<span style="color:red">%s</span>""" % line
    return line
