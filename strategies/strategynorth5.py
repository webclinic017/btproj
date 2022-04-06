import datetime

from backtrader.indicators import Stochastic, SmoothedMovingAverage

import loader
from strategies.one_order_strategy import OneOrderStrategy


# 以超卖行为作为止损点
class StrategyNorth5(OneOrderStrategy):
    params = (
        ('market', 'sh'),
        ('period', 500),
        ('highpercentstrong', 0.8),
        ('lowpercentstrong', 0.2),
        ('maxdrawbackstrong', 0.05),
        ('highpercentweak', 0.7),
        ('lowpercentweak', 0.4),
        ('maxdrawbackweak', 0.1),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single(self.params.market)
        self.sto = Stochastic(lowerband=20)
        self.sma = SmoothedMovingAverage(period=200)

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

        stoK = self.sto.lines.percK[0]
        stoD = self.sto.lines.percD[0]
        # if stoK >= stoD:
        if self.data.close[0] > self.sma[0]:
            highpercent = self.params.highpercentstrong
            lowpercent = self.params.lowpercentstrong
            maxdrawback = self.params.maxdrawbackstrong
        else:
            highpercent = self.params.highpercentweak
            lowpercent = self.params.lowpercentweak
            maxdrawback = self.params.maxdrawbackweak

        (north_value_today, north_value_low, north_value_high) \
            = self.get_north_position(north_history, lowpercent, highpercent)

        has_position = True if self.getposition() else False
        self.log('%s / Today %.3f / Low %.3f / High %.5f / StoK %.3f / StoD %.3f' % (
            has_position, north_value_today, north_value_low, north_value_high, stoK, stoD))

        if has_position:
            # if north_value_today < north_value_low or self.data.close[0] < self.buy_price * (1 - self.params.maxdrawback):
            # if north_value_today < north_value_low or self.sto.lines.percK[0] < self.sto.params.lowerband:
            if north_value_today < north_value_low or (
                    self.data.close[0] < self.buy_price * (1 - maxdrawback) and stoK >= self.sto.params.lowerband):
                self.sell_stock()
        else:
            if north_value_today > north_value_high:
                self.buy_stock()

    def get_north_position(self, north_history, lowpercent, highpercent):
        north_value_today = north_history.iloc[-1]['value']

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * lowpercent)]['value']
        north_value_high = north_history.iloc[int(history_len * highpercent)]['value']

        return north_value_today, north_value_low, north_value_high
