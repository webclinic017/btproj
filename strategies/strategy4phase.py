from backtrader.indicators import MovingAverageSimple, RelativeStrengthIndex

from strategies.base import get_data_name
from strategies.one_order_strategy import OneOrderStrategy


REASON_MAIN = 1
REASON_SUPERLOW = 2


class Strategy4Phase(OneOrderStrategy):
    params = (
        ('buyperiod', 18),
        ('sellperiod', 22),
        ('minchgpct', 0),
        ('shouldbuypct', 0),
        ('starttradedt', None),
        ('halfrate', 50),
        ('backdays', 3),
        ('mode', 2),
        ('rsi', None),
        ('printlog', True),
        ('opt', False)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.count = 0
        self.next_buy_index_2 = None
        self.half = False

        if type(self.params.rsi) is str:
            self.rsi_param = eval(self.params.rsi)
        else:
            self.rsi_param = self.params.rsi

        self.sma_list = []
        self.rsi_list = []
        for index in range(len(self.datas)):
            data = self.datas[index]
            if not self.params.opt:
                if self.params.buyperiod == self.params.sellperiod:
                    self.sma_list.append(MovingAverageSimple(data, period=self.params.buyperiod))
                else:
                    self.sma_list.append(MovingAverageSimple(data, period=self.params.buyperiod))
                    self.sma_list.append(MovingAverageSimple(data, period=self.params.sellperiod))
            if self.p.mode != 1:
                self.rsi_list.append(RelativeStrengthIndex(data, lowerband=self.rsi_param[index][0]))

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

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

        current_position = -1
        has_operation = False

        for index in range(len(self.datas)):
            data = self.datas[index]
            if self.getposition(data=data):
                self.log("has position %d" % index)
                current_position = index
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
                if self.buy_reason == REASON_SUPERLOW:
                    should_sell = False

                if should_sell:
                    next_buy_index = None if not should_buy else buy_best_index
                    self.sell_stock(index, sell_reason=REASON_MAIN)
                    has_operation = True
                    self.half = False
                    self.next_buy_index_2 = next_buy_index
                    if self.next_buy_index_2 is not None:
                        self.log('next_buy %d' % self.next_buy_index_2)
        if current_position == -1:
            buy_index = buy_best_index if buy_best_change > self.params.shouldbuypct / 100 else self.next_buy_index_2
            self.half = False
            if buy_index is not None:
                size = None
                if self.datas[buy_index].close[0] < self.datas[buy_index].close[-self.p.backdays]:
                    size = int(self.broker.get_cash() / self.p.halfrate / self.datas[buy_index].close[0])
                    self.half = True
                    self.log('first half')

                if self.next_buy_index_2 is not None and self.next_buy_index_2 != buy_index:
                    self.log('next_buy_index_2 %d, buy_index %d' % (self.next_buy_index_2, buy_index))
                self.buy_stock(buy_index, size=size, buy_reason=REASON_MAIN)
                has_operation = True
        elif self.half:
            buy_index = buy_best_index if buy_best_change > self.params.shouldbuypct / 100 else self.next_buy_index_2
            if buy_index == current_position:
                size = int(self.broker.get_cash() / self.datas[buy_index].close[0] * 0.95)
                self.log('second half')
                self.buy_stock(buy_index, size=size, buy_reason=REASON_MAIN)
                self.half = False

        if self.p.mode == 2 or self.p.mode == 3:
            if not has_operation:
                if current_position == -1:
                    buy_index = self.calculate_rsi()
                    if buy_index is not None:
                        self.buy_stock(buy_index, buy_reason=REASON_SUPERLOW)
                else:
                    if self.buy_reason == REASON_SUPERLOW and self.in_market_days >= self.rsi_param[current_position][1]:
                        self.sell_stock(current_position, sell_reason=REASON_SUPERLOW)

    def calculate_changes(self, period, usecase):
        changes = []
        logs = []
        best_index = -1
        best_change = -100000
        logs.append("Usecase: %s " % usecase)
        logs.append("Period: %d " % period)
        for index in range(len(self.datas)):
            data = self.datas[index]
            close_now = data.close[0]
            close_before = data.close[-period]
            change = (close_now - close_before) / close_before
            changes.append(change)
            if self.p.mode != 1:
                rsi = self.rsi_list[index][0]
                logs.append('%s / TodayClose %.3f / Change %.3f%% / RSI %.3f' % (get_data_name(data), close_now, change * 100, rsi))
            else:
                logs.append('%s / TodayClose %.3f / Change %.3f%%' % (get_data_name(data), close_now, change * 100))
            if change > best_change:
                best_change = change
                best_index = index
        logs.append('Best Index: %d' % best_index)
        next_log = ", ".join(logs)
        self.last_next_log = next_log
        self.log(next_log)
        return changes, best_change, best_index

    def calculate_rsi(self):
        if self.p.mode == 2:
            for index in range(len(self.datas)):
                rsi = self.rsi_list[index][0]
                rsi1 = self.rsi_list[index][-1]
                if rsi <= self.rsi_param[index][0] < rsi1:
                    return index
        if self.p.mode == 3:
            best_index = None
            lowest_rsi = 100
            for index in range(len(self.datas)):
                rsi = self.rsi_list[index][0]
                rsi1 = self.rsi_list[index][-1]
                if rsi <= self.rsi_param[index][0] < rsi1:
                    if rsi < lowest_rsi:
                        best_index = index
                        lowest_rsi = rsi
            if best_index is not None:
                return best_index
        return None

    def buy_stock(self, buy_index=0, buy_reason=0, size=None):
        OneOrderStrategy.buy_stock(self, buy_index=buy_index, buy_reason=buy_reason, size=size)
        self.next_buy_index_2 = None
