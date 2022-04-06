import datetime

import loader
from strategies.one_order_strategy import OneOrderStrategy

# 多阶段StrategyNorth
class StrategyNorth3(OneOrderStrategy):
    params = (
        ('market', 'sh'),
        ('phase', 2),
        ('period', 500),
        ('highpercent', 0.8),
        ('lowpercent', 0.2),
        ('maxdrawback', 0.05),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single(self.params.market)
        self.current_phase = 0

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        if self.order:
            return

        today = self.datas[0].datetime.date()
        if self.params.period > 0:
            start_day = today - datetime.timedelta(days=self.params.period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        if north_history.iloc[-1]['date_raw'] != today.__str__():
            self.log('no data for today, skip')
            return

        north_value_today = north_history.iloc[-1]['value']

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * self.params.lowpercent)]['value']
        north_value_high = north_history.iloc[int(history_len * self.params.highpercent)]['value']

        has_position = True if self.getposition() else False
        self.log('%s / Today %.3f / Low %.3f / High %.5f' % (
            has_position, north_value_today, north_value_low, north_value_high))

        if has_position and (north_value_today < north_value_low or self.data.close[0] < self.buy_price * (1 - self.params.maxdrawback)):
            self.sell_stock()
            self.current_phase = 0
        elif north_value_today > north_value_high:
            if self.current_phase < self.params.phase:
                size = int(self.broker.get_cash() / (self.params.phase - self.current_phase) / self.data.close[0])
                size = int(size / 100 * 0.95) * 100
                self.buy_stock(size=size)
                self.current_phase = self.current_phase + 1


