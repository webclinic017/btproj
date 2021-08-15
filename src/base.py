import json

import backtrader as bt


def get_data_name(data):
    return data._name


class BaseStrategy(bt.Strategy):

    def log(self, txt, dt=None, doprint=False):
        """ Logging function fot this strategy"""
        if doprint or self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, %s, GROSS %.3f, NET %.3f' %
                 (get_data_name(trade.data), trade.pnl, trade.pnlcomm))

    def stop(self):
        self.log('%s Ending Value %.3f' %
                 (json.dumps(self.params.__dict__), self.broker.getvalue()), doprint=True)