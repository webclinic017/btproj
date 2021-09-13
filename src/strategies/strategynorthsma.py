import datetime

from backtrader.indicators import SmoothedMovingAverage

import loader
from strategies.one_order_strategy import OneOrderStrategy


class StrategyNorthWithSMA(OneOrderStrategy):
    params = (
        ('periodbull', 500),
        ('highpercentbull', 0.8),
        ('lowpercentbull', 0.2),
        ('maxdrawbackbull', 0.05),
        ('periodbear', 60),
        ('highpercentbear', 0.9),
        ('lowpercentbear', 0.4),
        ('maxdrawbackbear', 0.1),
        ('smaperiod', 120),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single('sh')
        self.sma = SmoothedMovingAverage(period=self.params.smaperiod)

    def next(self):
        if self.order:
            return

        if self.data.close[0] >= self.sma[0]:
            self.do_next(self.params.periodbull, self.params.highpercentbull, self.params.lowpercentbull,
                         self.params.maxdrawbackbull)
        else:
            self.do_next(self.params.periodbear, self.params.highpercentbear, self.params.lowpercentbear,
                         self.params.maxdrawbackbear)

    def do_next(self, period, highp, lowp, maxd):
        # north_history = self.north_history['2016-12-05':self.datas[0].datetime.date()]
        today = self.datas[0].datetime.date()
        if period > 0:
            start_day = today - datetime.timedelta(days=period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        north_value_today = north_history.iloc[-1]['value']

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * lowp)]['value']
        north_value_high = north_history.iloc[int(history_len * highp)]['value']

        has_position = True if self.getposition() else False
        self.log('%s / Today %.3f / Low %.3f / High %.5f' % (
            has_position, north_value_today, north_value_low, north_value_high))

        # if has_position:
        #     if north_value_today < north_value_low and self.macd.lines.macd < self.macd.lines.signal:
        #         self.sell_stock()
        # else:
        #     if north_value_today > north_value_high and self.macd.lines.macd > self.macd.lines.signal:
        #         self.buy_stock()

        if has_position:
            if north_value_today < north_value_low or self.data.close[0] < self.buy_price * (
                    1 - maxd):
                # if north_value_today < north_value_low:
                self.sell_stock()
        else:
            if north_value_today > north_value_high:
                self.buy_stock()
