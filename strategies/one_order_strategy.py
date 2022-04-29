from backtrader import Order

from strategies.base import BaseStrategy, get_data_name


class OneOrderStrategy(BaseStrategy):

    def __init__(self):
        BaseStrategy.__init__(self)
        self.order = None
        self.buy_price = None
        self.next_buy_index = None
        self.last_order_log = None
        self.last_next_log = None
        self.in_market_days = 0
        self.buy_reason = 0
        self.sell_reason = 0

    def next(self):
        in_market = False
        for index in range(len(self.datas)):
            data = self.datas[index]
            if self.getposition(data=data):
                in_market = True
                break
        if in_market:
            self.in_market_days = self.in_market_days + 1
        else:
            self.in_market_days = 0

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
                self.buy_price = order.executed.price
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.3f, Size: %d, Cost: %.3f, Comm %.3f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.buy_price = None
                if self.next_buy_index is not None:
                    self.buy_stock(self.next_buy_index)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order ' + order.Status[order.status])

    def buy_stock(self, buy_index=0, size=None, buy_reason=0):
        data = self.datas[buy_index]
        log_txt = 'BUY CREATE %s, %.3f, SIZE %s, BUYREASON %d' % (get_data_name(data), data.close[0], str(size), buy_reason)
        self.log(log_txt)
        self.buy_reason = buy_reason
        self.order = self.buy(data, size=size, valid=Order.DAY)
        self.next_buy_index = None
        self.last_order_log = self.log_text(log_txt)

    def sell_stock(self, sell_index=0, next_buy_index=None, size=None, sell_reason=0):
        data = self.datas[sell_index]
        log_txt = 'SELL CREATE %s, %.3f, NEXT BUY %s, SIZE %s, SELLREASON %d' % (get_data_name(data), data.close[0], next_buy_index, str(size), sell_reason)
        self.log(log_txt)
        self.sell_reason = sell_reason
        self.order = self.sell(data, size=size, valid=Order.DAY)
        self.next_buy_index = next_buy_index
        self.last_order_log = self.log_text(log_txt)

    def stop(self):
        BaseStrategy.stop(self)
        if self.last_order_log is not None:
            self.log('Last Order: ' + self.last_order_log, doprint=True)
        if self.last_next_log is not None:
            self.log('Last Log: ' + self.last_next_log, doprint=True)
