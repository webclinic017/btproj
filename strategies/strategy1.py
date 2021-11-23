from strategies.base import get_data_name
from strategies.one_order_strategy import OneOrderStrategy


class Strategy1(OneOrderStrategy):
    params = (
        ('maperiod', 20),
        ('minchgpct', 1),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.count = 0

    def next(self):
        if self.count <= self.params.maperiod:
            self.count += 1
            return

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        changes, best_change, best_index = self.calculate_changes()
        has_position = False

        for index in range(len(self.datas)):
            data = self.datas[index]
            if self.getposition(data=data):
                has_position = True
                should_sell = True
                if best_index == index:
                    should_sell = False
                elif (best_change - changes[index]) < self.params.minchgpct / 100:
                    should_sell = False

                if should_sell:
                    next_buy_index = best_index
                    if best_change < 0:
                        next_buy_index = None
                    self.sell_stock(index, next_buy_index)
        if not has_position:
            if best_change > 0:
                self.buy_stock(best_index)

    def calculate_changes(self):
        changes = []
        logs = []
        best_index = -1
        best_change = -100000
        for index in range(len(self.datas)):
            data = self.datas[index]
            close_now = data.close[0]
            close_before = data.close[-self.params.maperiod]
            change = (close_now - close_before) / close_before
            changes.append(change)
            logs.append('%s / CloseBefore %.3f / CloseNow %.3f / Change %.5f' % (
                get_data_name(data), close_before, close_now, change))
            if change > best_change:
                best_change = change
                best_index = index
        logs.append('Best Index: %d' % best_index)
        self.log(", ".join(logs))
        return changes, best_change, best_index
