import datetime

from backtrader import Order

import loader
from base import get_data_name, BaseStrategy


class StrategyNorth(BaseStrategy):
    params = (
        ('period', 500),
        ('highpercent', 0.8),
        ('lowpercent', 0.2),
        ('printlog', True)
    )

    def __init__(self):
        self.north_history = loader.load_north_single('sh')
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        self.order = None

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.3f, Size: %d, Cost: %.3f, Comm %.3f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.3f, Size: %d, Cost: %.3f, Comm %.3f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order ' + order.Status[order.status])

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

        if has_position:
            if north_value_today < north_value_low:
                self.sell_stock()
        else:
            if north_value_today > north_value_high:
                self.buy_stock()

    def buy_stock(self):
        data = self.datas[0]
        self.log('BUY CREATE %s, %.3f' % (get_data_name(data), data.close[0]))
        self.order = self.buy(data, valid=Order.DAY, exectype=Order.Market)

    def sell_stock(self):
        data = self.datas[0]
        self.log('SELL CREATE %s, %.3f' % (get_data_name(data), data.close[0]))
        self.order = self.sell(data, valid=Order.DAY, exectype=Order.Market)
