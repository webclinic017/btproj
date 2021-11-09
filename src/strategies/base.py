import json

import backtrader as bt


def get_data_name(data):
    return data._name


class BaseStrategy(bt.Strategy):

    def __init__(self):
        bt.Strategy.__init__(self)
        self.logs = []

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

    def stop(self):
        self.log('%s Ending Value %.3f' %
                 (json.dumps(self.params.__dict__), self.broker.getvalue()), doprint=True)
