from backtrader import Order

from base import get_data_name, BaseStrategy


class Strategy2(BaseStrategy):
    params = (
        ('buyperiod', 20),
        ('sellperiod', 20),
        ('minchgpct', 1),
        ('printlog', True)
    )

    def __init__(self):
        self.order = None
        self.next_buy_index = None
        self.count = 0

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
                if self.next_buy_index is not None:
                    self.buy_stock(self.next_buy_index)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order ' + order.Status[order.status])

    def next(self):
        if self.count <= max(self.params.buyperiod, self.params.sellperiod):
            self.count += 1
            return

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        buy_changes, buy_best_change, buy_best_index = self.calculate_changes(self.params.buyperiod, 'Buy')
        sell_changes, sell_best_change, sell_best_index = self.calculate_changes(self.params.sellperiod, 'Sell')
        has_position = False

        for index in range(len(self.datas)):
            data = self.datas[index]
            if self.getposition(data=data):
                self.log("has position %d" % index)
                has_position = True
                should_buy = buy_best_change > 0
                should_sell = True
                # if best_index == index:
                #     should_sell = False
                if sell_best_index != index and (sell_best_change - sell_changes[index]) < self.params.minchgpct / 100:
                    should_sell = False
                if should_sell and should_buy and buy_best_index == index:
                    should_sell = False

                if should_sell:
                    next_buy_index = buy_best_index
                    if not should_buy:
                        next_buy_index = None
                    self.sell_stock(index, next_buy_index)
        if not has_position:
            if buy_best_change > 0:
                self.buy_stock(buy_best_index)

    def calculate_changes(self, period, usecase):
        changes = []
        logs = []
        best_index = -1
        best_change = -100000
        logs.append("Usecase: %s" % usecase)
        for index in range(len(self.datas)):
            data = self.datas[index]
            close_now = data.close[0]
            close_before = data.close[-period]
            change = (close_now - close_before) / close_before
            changes.append(change)
            logs.append('%s / Period %d / CloseBefore %.3f / CloseNow %.3f / Change %.5f' % (
                get_data_name(data), period, close_before, close_now, change))
            if change > best_change:
                best_change = change
                best_index = index
        logs.append('Best Index: %d' % best_index)
        self.log(", ".join(logs))
        return changes, best_change, best_index

    def buy_stock(self, buy_index):
        data = self.datas[buy_index]
        self.log('BUY CREATE %s, %.3f' % (get_data_name(data), data.close[0]))
        self.order = self.buy(data, valid=Order.DAY)
        # self.order = self.buy(data, price=data.close[0], exectype=Order.Limit)
        self.next_buy_index = None

    def sell_stock(self, sell_index, next_buy_index):
        data = self.datas[sell_index]
        self.log('SELL CREATE %s, %.3f, NEXT BUY %s' % (get_data_name(data), data.close[0], next_buy_index))
        self.order = self.sell(data, valid=Order.DAY)
        self.next_buy_index = next_buy_index
