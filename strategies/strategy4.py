from backtrader.indicators import MovingAverageSimple, AdaptiveMovingAverage

from indicators.DonChainChannels import DonChainChannels
from strategies.base import get_data_name
from strategies.one_order_strategy import OneOrderStrategy


class Strategy4(OneOrderStrategy):
    params = (
        ('buyperiod', 20),
        ('sellperiod', 20),
        ('minchgpct', 0),
        ('shouldbuypct', 0.7),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.count = 0
        self.next_buy_index_2 = None

        self.sma_list = []
        self.ama_list = []
        for index in range(len(self.datas)):
            data = self.datas[index]
            self.sma_list.append(MovingAverageSimple(data, period=self.params.sellperiod))
            self.ama_list.append(AdaptiveMovingAverage(data, slow=self.params.sellperiod))

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

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
                should_buy = buy_best_change > self.params.shouldbuypct / 100
                should_sell = True
                if sell_best_index != index and (sell_best_change - sell_changes[index]) < self.params.minchgpct / 100:
                    should_sell = False
                # if should_sell and should_buy and buy_best_index == index:
                if buy_best_index == index:
                    should_sell = False
                if sell_changes[index] < 0:
                    should_sell = True
                    if buy_best_index == index:
                        buy_best_index = None

                if should_sell:
                    next_buy_index = buy_best_index
                    if not should_buy:
                        next_buy_index = None
                    self.sell_stock(index)
                    self.next_buy_index_2 = next_buy_index
                    if self.next_buy_index_2 is not None:
                        self.log('next_buy %d' % (self.next_buy_index_2))
        if not has_position:
            buy_index = self.next_buy_index_2
            if buy_best_change > self.params.shouldbuypct / 100:
                buy_index = buy_best_index
            if buy_index is not None:
                if self.next_buy_index_2 is not None and self.next_buy_index_2 != buy_index:
                    self.log('next_buy_index_2 %d, buy_index %d' % (self.next_buy_index_2, buy_index))
                self.buy_stock(buy_index)

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

    def buy_stock(self, buy_index=0):
        OneOrderStrategy.buy_stock(self, buy_index)
        self.next_buy_index_2 = None
