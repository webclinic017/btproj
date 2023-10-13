import datetime
import gc
import pathlib
import threading
import time
from dataclasses import dataclass

import pytz
import pandas as pd

import backtrader as bt
import matplotlib
import quantstats
import schedule
from backtrader.observers import Broker, BuySell, Trades, DataTrades
from backtrader_plotting import Bokeh
from flask import Flask, stream_with_context, request, render_template

import stocks
from appstrategies import get_strategies
from loader import load_stock_data, force_load_north, get_datafile_name, date_ahead, force_load_stock_history_2, \
    force_load_etf_accu_history, force_load_investigation, load_stock_history, load_north_single
from oberservers.RelativeValue import RelativeValue
from strategies.base import get_data_name
from strategies.strategydisplay import StrategyDisplay

app = Flask(__name__)

last_update_time = "N/A"

@app.route("/")
def home():
    return render_template('index.html', strategies=get_strategies())


@app.route("/updatetime")
def updatetime():
    global last_update_time
    template = """Now: %s<br>
Last update: %s"""
    return template % (format_time(), last_update_time)


@app.route("/daily")
def daily_strategy():
    coreonly = request.args.get('coreonly', default="False")
    (start_date, end_date, start_trade_date) = get_request_dates()
    logs = []
    for strategy_id, strategy in enumerate(get_strategies()):
        if coreonly != 'True' or strategy["core"]:
            logs.append(make_link(strategy["label"], "log/%d" % strategy_id))
            for stock in strategy["stocks"]:
                logs.append(make_link(stock.cnname, "dataplot/%s?accu=False" % stock.code))
            if strategy["core"]:
                logs.append('*')
            try:
                logs = logs + run(strategy["class"], strategy["stocks"], start=start_date, end=end_date,
                                  data_start=strategy["data_start"], starttradedt=start_trade_date,
                                  time_frame=strategy.get('time_frame'), **strategy["args"])
            except:
                logs.append("Error. Maybe no data in this period.")
            logs.append('')
    logs = list(map(lambda line: decorate_line(line), logs))

    global last_update_time
    return render_template('daily_strategy.html',
                           start_date=format_none(start_date),
                           end_date=format_none(end_date),
                           start_trade_date=format_none(start_trade_date),
                           coreonly=format_none(coreonly),
                           logs=logs,
                           time_now=format_time(),
                           time_last_update=last_update_time)


@app.route("/log/<int:id>")
def daily_strategy_logs(id):
    strategy = get_strategies()[id]
    if strategy.get("start_date") is None:
        (start_date, end_date, start_trade_date) = get_request_dates()
    else:
        (start_date, end_date, start_trade_date) = get_request_dates(default_start_date=strategy.get("start_date"))
    preview = eval(request.args.get('preview', default="False"))

    logs = [strategy["label"]]
    logs = logs + run(strategy["class"], strategy["stocks"], start=start_date, end=end_date,
                      data_start=strategy["data_start"], time_frame=strategy.get('time_frame'),
                      starttradedt=start_trade_date, printLog=True, preview=preview,
                      **strategy["args"])
    logs = list(map(lambda line: decorate_line(line), logs))

    return render_template('daily_strategy_logs.html',
                           id=id,
                           start_date=format_none(start_date),
                           end_date=format_none(end_date),
                           start_trade_date=format_none(start_trade_date),
                           preview=str(preview),
                           logs=logs)


@app.route("/plot/<int:id>", defaults={'start_date': '2022-12-30', 'end_date': None})
@app.route('/plot/<int:id>/<string:start_date>', defaults={'end_date': None})
@app.route('/plot/<int:id>/<string:start_date>/<string:end_date>')
def daily_strategy_plot(id, start_date, end_date):
    strategy = get_strategies()[id]
    if start_date == '2022-12-30' and strategy.get("start_date") is not None:
        start_date = strategy.get("start_date")
    html = run_plot(strategy["class"], strategy["stocks"], start=start_date, end=end_date,
                    data_start=strategy["data_start"], time_frame=strategy.get("time_frame"),
                    starttradedt=start_date, printLog=False, **strategy["args"])
    return html


@app.route("/pyfolio/<int:id>", defaults={'start_date': '2017-01-01', 'end_date': None})
@app.route('/pyfolio/<int:id>/<string:start_date>', defaults={'end_date': None})
@app.route('/pyfolio/<int:id>/<string:start_date>/<string:end_date>')
def daily_strategy_pyfolio(id, start_date, end_date):
    benchmark_idx = eval(request.args.get('benchmark', default='0'))
    strategy = get_strategies()[id]
    html = run_pyfolio(id, strategy["class"], strategy["stocks"], start=start_date, end=end_date,
                       data_start=strategy["data_start"], time_frame=strategy.get("time_frame"),
                       starttradedt=start_date, printLog=False, title=strategy["label"], benchmark_idx=benchmark_idx,
                       **strategy["args"])
    return html


@app.route("/multipyfolio")
def daily_multi_pyfolio():
    ids_str = request.args.get('ids')
    start_date, end_date, _ = get_request_dates()
    ids = list(map(int, ids_str.split(",")))
    html = run_multi_pyfolio(ids=ids, start=start_date, end=end_date, starttradedt=start_date, printLog=False)
    return html


@app.route("/load")
def load():
    coreonly = request.args.get('coreonly', default="False")
    types = request.args.get('types', default="all")

    gc.collect()

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
                if types == 'all' or types == 'value':
                    history = force_load_stock_history_2(stock.code)
                    date = str(history.iloc[-1]['date'])
                    close_today = history.iloc[-1]['close']
                    close_yesterday = history.iloc[-2]['close'] if len(history) >= 2 else close_today
                    change_rate = round((close_today - close_yesterday) / close_yesterday * 100, 2)
                    color = 'red' if change_rate >= 0 else 'green'
                    yield '<tr><td>%s %s</td><td>%s</td><td>loaded</td><td>%s</td><td style="color:%s">%s%%</td></tr>' \
                        % (stock.code, stock.cnname, date, str(close_today), color, str(change_rate))
                if types == 'all' or types == 'accu':
                    if not stock.is_index:
                        accu_history = force_load_etf_accu_history(stock.code)
                        date = str(accu_history.iloc[-1]['date'])
                        yield '<tr><td>%s %s</td><td>%s</td><td>accu loaded</td><td>%s</td></tr>' \
                            % (stock.code, stock.cnname, date, str(accu_history.iloc[-1]['accu_qfq']))

        if types == 'all' or types == 'value':
            north_results = force_load_north()
            for north_result in north_results:
                north_item = north_result[0]
                history = north_result[1]
                today = history.iloc[-1]
                yield ('<tr><td>%s</td><td>%s</td><td>loaded</td><td>%s</td></tr>'
                       % (north_item[1], str(today['date']), str(today['value'])))
            global last_update_time
            last_update_time = format_time()

        if types == 'all' or types == 'investigation':
            investigation_history = force_load_investigation()
            yield '<tr><td>机构调研</td><td>%s</td><td>loaded</td></tr>' % (
                str(investigation_history["公告日期"].iloc[0]))

        yield '</table></div>'
        yield '<div>Finished</div>'
        yield """</body></html>"""

    return app.response_class(stream_with_context(generate()))


@app.route("/datalist")
def datalist():
    coreonly = request.args.get('coreonly', default="False")

    @dataclass
    class StockData:
        stock: stocks.Stock
        date: str
        close_today: float
        change_rate: float
        change_rate_color: str

    @dataclass
    class NorthData:
        market: str
        name: str
        date: str
        value: float

    stock_list = []
    for stock in stocks.Stock:
        if coreonly != 'True' or stock.core:
            history = load_stock_history(stock.code)
            date = history['date_raw'].iloc[-1]
            close_today = history['close'].iloc[-1]
            close_yesterday = history['close'].iloc[-2] if len(history) >= 2 else close_today
            change_rate = round((close_today - close_yesterday) / close_yesterday * 100, 2)
            change_rate_color = 'red' if change_rate >= 0 else 'green'
            stock_list.append(StockData(stock, date, close_today, change_rate, change_rate_color))

    north_list = []
    for market in ['all', 'sh', 'sz']:
        history = load_north_single(market)
        date = history['date_raw'].iloc[-1]
        value = history['value'].iloc[-1]
        north_list.append(NorthData(market, 'North ' + market.upper(), date, value))

    return render_template('datalist.html', stock_list=stock_list, north_list=north_list)


@app.route("/data/<stock_code>", defaults={'rows': 30})
@app.route('/data/<stock_code>/<int:rows>')
def data(stock_code, rows):
    reverse = request.args.get('reverse', default="True")

    stock = get_stock(stock_code)

    lines = pathlib.Path(get_datafile_name(stock_code)).read_text().split("\n")
    lines = list(filter(lambda l: len(l) > 0, lines))
    if reverse == 'True':
        lines = [lines[0]] + lines[-rows:][::-1]
    else:
        lines = lines[:rows + 1]
    lines = list(map(lambda l: l.split(","), lines))

    return render_template('data.html', stock=stock, stock_code=stock_code, lines=lines)


@app.route("/dataplot/<stock_code>", defaults={'start_date': None, 'end_date': None})
@app.route('/dataplot/<stock_code>/<string:start_date>', defaults={'end_date': None})
@app.route('/dataplot/<stock_code>/<string:start_date>/<string:end_date>')
def dataplot(stock_code, start_date, end_date):
    show_sma = eval(request.args.get('sma', default="True"))
    show_rsi = eval(request.args.get('rsi', default="True"))
    show_macd = eval(request.args.get('macd', default="True"))
    show_accu = eval(request.args.get('accu', default="True"))

    if start_date is None:
        today = datetime.date.today()
        start_date = str(today - datetime.timedelta(days=7300))
    stock = get_stock(stock_code)
    html = run_data_plot(stock, start=start_date, end=end_date, show_accu=show_accu, show_sma=show_sma,
                         show_rsi=show_rsi, show_macd=show_macd, stock_code=stock.code)
    return html


@app.route("/datapyfolio/<stock_code>", defaults={'start_date': '2017-01-01', 'end_date': None})
@app.route('/datapyfolio/<stock_code>/<string:start_date>', defaults={'end_date': None})
@app.route('/datapyfolio/<stock_code>/<string:start_date>/<string:end_date>')
def datapyfolio(stock_code, start_date, end_date):
    stock = get_stock(stock_code)
    html = run_data_pyfolio(stock, start=start_date, end=end_date, show_accu=False, show_sma=False,
                            show_rsi=False, show_macd=False, stock_code=stock.code)
    return html


def run(strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False, preview=False,
        time_frame=None, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    start = parse_empty(start)
    end = parse_empty(end)
    starttradedt = parse_empty(starttradedt)
    if starttradedt is None:
        starttradedt = start

    cerebro.addstrategy(strategy_class, printlog=printLog, starttradedt=starttradedt, **kwargs)

    datas, _ = load_stock_data(cerebro, stocks, date_ahead(start, data_start), end, time_frame=time_frame, preview=preview)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    if len(datas) == 1:
        cerebro.addobserver(Trades)
    else:
        cerebro.addobserver(DataTrades)

    logs = [str(strategy_class.__name__), 'Starting Portfolio Value: %.3f' % cerebro.broker.getvalue()]

    cerebro.run()
    logs = logs + cerebro.runstrats[0][0].logs

    logs.append('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())

    return logs


def run_plot(strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False,
             time_frame=None, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    if starttradedt is None:
        starttradedt = start

    cerebro.addstrategy(strategy_class, printlog=printLog, starttradedt=starttradedt, **kwargs)

    load_stock_data(cerebro, stocks, date_ahead(start, data_start), end, time_frame=time_frame)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.addobserver(Broker)
    cerebro.addobservermulti(BuySell, bardist=0)
    cerebro.addobservermulti(RelativeValue, starttradedt=starttradedt)
    if len(stocks) == 1:
        cerebro.addobserver(Trades)
    else:
        cerebro.addobserver(DataTrades)

    cerebro.run()

    folder = 'plot'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    filename = folder + '/app.html'

    b = Bokeh(style='bar', plot_mode='single', filename=filename, show=False, output_mode='save')
    cerebro.plot(b)

    return pathlib.Path(filename).read_text()


def run_pyfolio(id, strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False, title=None,
                benchmark_idx=0, time_frame=None, **kwargs):
    datas, dfs, returns = run_returns(strategy, stocks, start, end, data_start, starttradedt, printLog,
                                      time_frame=time_frame, **kwargs)

    folder = 'report'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    filename = folder + '/pyfolio_' + str(id) + '_' + str(benchmark_idx) + '.html'

    matplotlib.pyplot.switch_backend('Agg')

    quantstats.reports.html(
        returns,
        benchmark=dfs[benchmark_idx]['close'],
        benchmark_title=get_data_name(datas[benchmark_idx]),
        output=filename,
        # download_filename=filename,
        title=title)

    return pathlib.Path(filename).read_text()


def run_multi_pyfolio(ids=None, start=None, end=None, starttradedt=None, printLog=False):
    returns_list = dict()
    sub_titles = ['Multi Strategies']
    for id in ids:
        strategy = get_strategies()[id-1]
        _, _, returns = run_returns(strategy["class"], strategy["stocks"], start, end, strategy["data_start"],
                                    starttradedt, printLog, time_frame=strategy.get("time_frame"), **strategy["args"])
        returns_list[str(id)] = returns
        sub_titles.append('%d: %s' % (id, strategy['label']))

    returns_df = pd.concat(returns_list, axis=1)
    returns_df.fillna(value=0, inplace=True)

    folder = 'report'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    filename = folder + '/multi_pyfolio.html'

    matplotlib.pyplot.switch_backend('Agg')

    quantstats.reports.html(
        returns_df,
        output=filename,
        # download_filename=filename,
        title="<br/>".join(sub_titles))

    return pathlib.Path(filename).read_text()


def run_returns(strategy, stocks, start=None, end=None, data_start=0, starttradedt=None, printLog=False,
                time_frame=None, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    strategy_class = strategy

    start = parse_empty(start)
    end = parse_empty(end)
    starttradedt = parse_empty(starttradedt)
    if starttradedt is None:
        starttradedt = start

    cerebro.addstrategy(strategy_class, printlog=printLog, starttradedt=starttradedt, **kwargs)

    datas, dfs = load_stock_data(cerebro, stocks, date_ahead(start, data_start), end, time_frame=time_frame)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    results = cerebro.run()

    portfolio_stats = results[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    return datas, dfs, returns


def run_data_plot(stock, start=None, end=None, data_start=0, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(StrategyDisplay, **kwargs)
    cerebro.addobserver(Broker)

    load_stock_data(cerebro, [stock], date_ahead(start, data_start), end)

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


def run_data_pyfolio(stock, start=None, end=None, data_start=0, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(StrategyDisplay, **kwargs)

    load_stock_data(cerebro, [stock], date_ahead(start, data_start), end)

    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=95)
    cerebro.broker.setcommission(commission=0.00025)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    results = cerebro.run()

    portfolio_stats = results[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    folder = 'report'
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    filename = folder + '/app.html'

    matplotlib.pyplot.switch_backend('Agg')

    quantstats.reports.html(
        returns,
        output=filename,
        # download_filename=filename,
        title=stock.cnname)

    return pathlib.Path(filename).read_text()


def get_stock(stock_code):
    for stock in stocks.Stock:
        if stock_code == stock.code:
            return stock
    return None


def decorate_line(line: str):
    if line.startswith('[LINK]'):
        items = line.split("|")
        text = items[1]
        link = items[2]
        return """<a class="sublink" href="%s">%s</a>""" % (link, text)
    if line.find('Last Order') > -1:
        if line.rfind(line[:10]) == 0:
            return """<span style="color:gray">%s</span>""" % line
    if line.find(' for ') > -1:
        return """<span style="color:blue">%s</span>""" % line
    if line.find('BUY CREATE') > -1 or line.find('BUY EXECUTED') > -1:
        return """<span style="color:green">%s</span>""" % line
    if line.find('OPERATION PROFIT') > -1 or line.find('SELL CREATE') > -1 or line.find('SELL EXECUTED') > -1:
        return """<span style="color:red">%s</span>""" % line
    if line.find('Last Log') > -1:
        return line.replace("TodayClose", """<span style="color:blue">TodayClose</span>""")
    return line


def format_none(o):
    if o is None:
        return ""
    return o


def parse_empty(s):
    if s == "":
        return None
    return s


def make_link(text, url):
    return '[LINK]|%s|%s' % (text, url)


def get_request_dates(default_start_date: str = "2022-12-30"):
    start_date = request.args.get('start', default=default_start_date)
    start_trade_date = request.args.get('start_trade_date', default=None)
    end_date = request.args.get('end', default=None)
    return start_date, end_date, start_trade_date


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def log(msg):
    print(format_time() + " " + msg)


def format_time():
    return datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S %Z")


def background_job():
    global last_update_time
    log('background_job start')
    try:
        gc.collect()
        for stock in stocks.Stock:
            force_load_stock_history_2(stock.code)
        force_load_north()
        last_update_time = format_time()
        log('background_job finish')
    except:
        log('background_job error')


schedule.every(30).minutes.do(background_job)

run_continuously(interval=60)
