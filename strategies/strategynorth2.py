import datetime

import loader
from strategies.one_order_strategy import OneOrderStrategy


class StrategyNorth2(OneOrderStrategy):
    params = (
        ('period', 500),
        ('highpercent', 0.6),
        ('lowpercent', 0.3),
        ('maxdrawback', 0.05),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_2_single('sh')

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        if self.order:
            return

        # north_history = self.north_history['2016-12-05':self.datas[0].datetime.date()]
        today = self.datas[0].datetime.date()
        if self.params.period > 0:
            start_day = today - datetime.timedelta(days=self.params.period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        if north_history.iloc[-1]['date_raw'] != today.__str__():
            self.log('no data for today, skip')
            return

        north_value_today = north_history.iloc[-1]['net_buy_vol']

        history_len = len(north_history)
        north_history.sort_values(by=['net_buy_vol'], inplace=True)
        north_value_low = north_history.iloc[int(history_len * self.params.lowpercent)]['net_buy_vol']

        north_history.sort_values(by=['net_in'], inplace=True)
        north_value_high = north_history.iloc[int(history_len * self.params.highpercent)]['net_in']

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
            if north_value_today < north_value_low or self.data.close[0] < self.buy_price * (1 - self.params.maxdrawback):
            # if north_value_today < north_value_low:
                self.sell_stock()
        else:
            if north_value_today > north_value_high:
                self.buy_stock()
