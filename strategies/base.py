import json

import backtrader as bt


def get_data_name(data):
    return data._name


class BaseStrategy(bt.Strategy):

    def __init__(self):
        bt.Strategy.__init__(self)
        self.logs = []
        self.trade_count = 0
        self.trade_count_win = 0
        self.first_day = True
        self.first_day_closes = []

    def log(self, txt, dt=None, doprint=False):
        """ Logging function fot this strategy"""
        if doprint or self.params.printlog:
            text = self.log_text(txt, dt)
            print(text)
            self.logs.append(text)

    def log_text(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        text = '%s, %s' % (dt.isoformat(), txt)
        return text

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, %s, GROSS %.3f, NET %.3f, DAYS %d' %
                 (get_data_name(trade.data), trade.pnl, trade.pnlcomm, (trade.dtclose - trade.dtopen)))
        self.trade_count = self.trade_count + 1
        if trade.pnlcomm >= 0:
            self.trade_count_win = self.trade_count_win + 1

    def stop(self):
        self.log('%s Ending Value %.3f, Trades: %d, Wins: %d' %
                 (json.dumps(self.params.__dict__), self.broker.getvalue(), self.trade_count, self.trade_count_win), doprint=True)
        last_day_log = 'Last Day, '
        for i in range(len(self.datas)):
            data = self.datas[i]
            self.first_day_closes.append(data.close[0])
            last_day_log = last_day_log + '%s: %.3f, ' % (get_data_name(data), data.close[0] / self.first_day_closes[i])
        self.log(last_day_log, doprint=True)

    def check_first_day(self):
        if self.first_day:
            first_day_log = 'First Day, '
            self.first_day = False
            for data in self.datas:
                self.first_day_closes.append(data.close[0])
                first_day_log = first_day_log + '%s: %.3f, ' % (get_data_name(data), data.close[0])
            self.log(first_day_log, doprint=True)
