import datetime

from backtrader.indicators import MACD, CrossOver, SmoothedMovingAverage

import loader
from strategies.one_order_strategy import OneOrderStrategy


class StrategyNorthWithSMA(OneOrderStrategy):
    params = (
        ('period', 500),
        ('smaperiod', 10),
        ('highpercent', 0.8),
        ('lowpercent', 0.2),
        ('maxdrawback', 0.05),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single('sh')
        self.sma = SmoothedMovingAverage(period=self.params.smaperiod)

    def next(self):
        if self.order:
            return

        # north_history = self.north_history['2016-12-05':self.datas[0].datetime.date()]
        today = self.datas[0].datetime.date()
        if self.params.period > 0:
            start_day = today - datetime.timedelta(days=self.params.period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        north_value_today = north_history.iloc[-1]['value']

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * self.params.lowpercent)]['value']
        north_value_high = north_history.iloc[int(history_len * self.params.highpercent)]['value']

        has_position = True if self.getposition() else False
        self.log('%s / Today %.3f / Low %.3f / High %.5f' % (
            has_position, north_value_today, north_value_low, north_value_high))

        # if has_position:
        #     if north_value_today < north_value_low and self.macd.lines.macd < self.macd.lines.signal:
        #         self.sell_stock()
        # else:
        #     if north_value_today > north_value_high and self.macd.lines.macd > self.macd.lines.signal:
        #         self.buy_stock()

        close0 = self.data.close[0]
        sma0 = self.sma[0]
        if has_position:
            if north_value_today < north_value_low \
                    or close0 < self.buy_price * (1 - self.params.maxdrawback):
                self.sell_stock()
        else:
            if north_value_today > north_value_high and close0 > sma0:
                self.buy_stock()
