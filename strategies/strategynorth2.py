import datetime

from backtrader.indicators import MovingAverageSimple

import loader
from strategies.one_order_strategy import OneOrderStrategy


class StrategyNorth2(OneOrderStrategy):
    params = (
        ('market', 'sh'),
        ('smaperiod', 25),
        ('period', 500),
        ('maxdrawback', 0.05),
        ('highpercent1', 0.8),
        ('lowpercent1', 0.2),
        ('highpercent2', 0.8),
        ('lowpercent2', 0.2),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single(self.params.market)
        self.sma = MovingAverageSimple(self.data, period=self.params.smaperiod)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        if self.order:
            return

        today = self.datas[0].datetime.date()
        # if self.north_history[:today].iloc[-1]['date_raw'] != today.__str__():
        #     self.log('no data for today, skip')
        #     return

        if self.data.close[0] < self.sma:
            self.process(self.params.period, self.params.highpercent1, self.params.lowpercent1,
                         self.params.maxdrawback, today)
        else:
            self.process(self.params.period, self.params.highpercent2, self.params.lowpercent2,
                         self.params.maxdrawback, today)

    def process(self, period, highpercent, lowpercent, maxdrawback, today):
        if period > 0:
            start_day = today - datetime.timedelta(days=period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        north_value_today = north_history.iloc[-1]['value']

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * lowpercent)]['value']
        north_value_high = north_history.iloc[int(history_len * highpercent)]['value']

        has_position = True if self.getposition() else False
        self.log('%s / Today %.3f / Low %.3f / High %.5f' % (
            has_position, north_value_today, north_value_low, north_value_high))

        if has_position:
            if north_value_today < north_value_low or self.data.close[0] < self.buy_price * (
                    1 - maxdrawback):
                # if north_value_today < north_value_low:
                self.sell_stock()
        else:
            if north_value_today > north_value_high:
                self.buy_stock()
