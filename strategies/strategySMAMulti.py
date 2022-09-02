from backtrader.indicators import MovingAverageSimple, RelativeStrengthIndex

from strategies.base import get_data_name
from strategies.one_order_strategy import OneOrderStrategy

REASON_MAIN = 1
REASON_SUPERLOW = 2
REASON_SUPERHIGH = 3


class StrategySMAMulti(OneOrderStrategy):
    params = (
        ('smaperiod', 30),
        ('daystobuy', 8),
        ('daystosell', 2),
        ('starttradedt', None),
        ('rsi', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)

        if type(self.params.rsi) is str:
            self.rsi_param = eval(self.params.rsi)
        else:
            self.rsi_param = self.params.rsi

        self.sma_list = []
        self.rsi_list = []
        for index in range(len(self.datas)):
            data = self.datas[index]
            self.sma_list.append(MovingAverageSimple(data, period=self.params.smaperiod))
            self.rsi_list.append(RelativeStrengthIndex(upperband=self.rsi_param[index][0], lowerband=self.rsi_param[index][1]))

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

        if self.order:
            return

        for index in range(len(self.datas)):
            has_operation = self.check(index)
            if has_operation:
                break

    def check(self, index):
        data = self.datas[index]
        sma = self.sma_list[index]
        rsi = self.rsi_list[index]
        has_position = True if self.getposition(data=data) else False

        daystosell = self.p.daystosell
        close_prices = data.close.get(size=daystosell)
        sma_prices = sma.get(size=daystosell)
        rsi0 = rsi[0]

        below_sma_count = 0
        for i in range(daystosell):
            if close_prices[i] < sma_prices[i]:
                below_sma_count = below_sma_count + 1

        daystobuy = self.p.daystobuy
        close_prices = data.close.get(size=daystobuy)
        sma_prices = sma.get(size=daystobuy)

        above_sma_count = 0
        for i in range(daystobuy):
            if close_prices[i] > sma_prices[i]:
                above_sma_count = above_sma_count + 1

        next_log = '%s / %s / Data %.3f / below SMA size %d / above SMA size %d / RSI %.3f' \
                   % (get_data_name(data), has_position, self.data.close[0], below_sma_count, above_sma_count, rsi0)
        self.last_next_log = next_log
        self.log(next_log)

        has_operation = False

        if has_position:
            all_below_sma = below_sma_count == daystosell
            if all_below_sma:
                self.sell_stock(index, sell_reason=REASON_MAIN)
                has_operation = True
        else:
            all_above_sma = above_sma_count == daystobuy
            if all_above_sma:
                self.buy_stock(index, buy_reason=REASON_MAIN)
                has_operation = True

        (rsihigh, rsilow, rsidays) = self.rsi_param[index]

        if not has_operation:
            if not has_position:
                rsi1 = rsi[-1]
                if rsi0 <= rsilow < rsi1:
                    self.buy_stock(index, buy_reason=REASON_SUPERLOW)
                    has_operation = True
            else:
                if self.buy_reason == REASON_SUPERLOW and self.in_market_days >= rsidays:
                    self.sell_stock(index, sell_reason=REASON_SUPERLOW)
                    has_operation = True

        if not has_operation:
            if has_position:
                rsi1 = rsi[-1]
                if rsi1 < rsihigh <= rsi0:
                    self.sell_stock(index, sell_reason=REASON_SUPERHIGH)
                    has_operation = True
            else:
                if self.sell_reason == REASON_SUPERHIGH and self.in_market_days >= rsidays:
                    self.buy_stock(index, buy_reason=REASON_SUPERHIGH)
                    has_operation = True

        return has_operation
