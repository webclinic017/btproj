from strategies.base import get_data_name
from strategies.one_order_strategy import OneOrderStrategy


class Strategy2(OneOrderStrategy):
    params = (
        ('buyperiod', 20),
        ('sellperiod', 10),
        ('minchgpct', 1),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.count = 0

    def next(self):
        if self.count <= max(self.params.buyperiod, self.params.sellperiod):
            self.count += 1
            return

        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if self.params.buyperiod == self.params.sellperiod:
            buy_changes, buy_best_change, buy_best_index \
                = sell_changes, sell_best_change, sell_best_index \
                = self.calculate_changes(self.params.buyperiod, 'BuySell')
        else:
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
