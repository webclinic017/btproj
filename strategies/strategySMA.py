from backtrader.indicators import RelativeStrengthIndex, MovingAverageSimple

from strategies.one_order_strategy import OneOrderStrategy


REASON_MAIN = 1
REASON_SUPERLOW = 2
REASON_SUPERHIGH = 3

class StrategySMA(OneOrderStrategy):

    params = (
        ('smaperiod', 30),
        ('daystobuy', 8),
        ('daystosell', 2),
        ('starttradedt', None),
        ('rsihigh', 74),
        ('rsilow', 25),
        ('rsidays', 5),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.sma = MovingAverageSimple(self.datas[0].close, period=self.params.smaperiod)
        self.rsi = RelativeStrengthIndex(upperband=self.params.rsihigh, lowerband=self.params.rsilow)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

        if self.order:
            return

        has_position = True if self.getposition() else False
        rsi = self.rsi[0]


        has_operation = False

        if has_position:
            daystosell = self.p.daystosell
            close_prices = self.data.close.get(size=daystosell)
            sma_prices = self.sma.get(size=daystosell)

            below_sma_count = 0
            for i in range(daystosell):
                if close_prices[i] < sma_prices[i]:
                    below_sma_count = below_sma_count + 1

            next_log = '%s / Data %.3f / below SMA size %d / RSI %.3f' \
                       % (has_position, self.data.close[0], below_sma_count, rsi)
            self.last_next_log = next_log
            self.log(next_log)

            all_below_sma = below_sma_count == daystosell
            if all_below_sma and self.buy_reason != REASON_SUPERLOW:
                self.sell_stock(sell_reason=REASON_MAIN)
                has_operation = True
        else:
            daystobuy = self.p.daystobuy
            close_prices = self.data.close.get(size=daystobuy)
            sma_prices = self.sma.get(size=daystobuy)

            above_sma_count = 0
            for i in range(daystobuy):
                if close_prices[i] > sma_prices[i]:
                    above_sma_count = above_sma_count + 1

            next_log = '%s / Data %.3f / above SMA size %d / RSI %.3f' \
                       % (has_position, self.data.close[0], above_sma_count, rsi)
            self.last_next_log = next_log
            self.log(next_log)

            all_above_sma = above_sma_count == daystobuy
            if all_above_sma:
                self.buy_stock(buy_reason=REASON_MAIN)
                has_operation = True

        if not has_operation:
            if not has_position:
                rsi1 = self.rsi[-1]
                if rsi <= self.params.rsilow < rsi1:
                    self.buy_stock(buy_reason=REASON_SUPERLOW)
                    has_operation = True
            else:
                if self.buy_reason == REASON_SUPERLOW and self.in_market_days >= self.params.rsidays:
                    self.sell_stock(sell_reason=REASON_SUPERLOW)
                    has_operation = True

        if not has_operation:
            if has_position:
                rsi1 = self.rsi[-1]
                if rsi1 < self.params.rsihigh <= rsi:
                    self.sell_stock(sell_reason=REASON_SUPERHIGH)
            else:
                if self.sell_reason == REASON_SUPERHIGH and self.in_market_days >= self.params.rsidays:
                    self.buy_reason(buy_reason=REASON_SUPERHIGH)
