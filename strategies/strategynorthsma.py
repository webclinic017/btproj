import datetime

from backtrader.indicators import RelativeStrengthIndex

import loader
from indicators.NorthInd import NorthValue
from strategies.one_order_strategy import OneOrderStrategy


REASON_MAIN = 1
REASON_SUPERLOW = 2
REASON_SUPERHIGH = 3


class StrategyNorthWithSMA(OneOrderStrategy):
    params = (
        ('market', 'sh'),
        ('periodbull', 500),
        ('highpercentbull', 0.8),
        ('lowpercentbull', 0.2),
        ('maxdrawbackbull', 0.05),
        ('periodbear', 60),
        ('highpercentbear', 0.9),
        ('lowpercentbear', 0.4),
        ('maxdrawbackbear', 0.1),
        ('smaperiod', 20),
        ('starttradedt', None),
        ('rsihigh', 80),
        ('rsilow', 25),
        ('rsidays', 5),
        ('mode', 3),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.north_history = loader.load_north_single(self.params.market)
        self.rsi = RelativeStrengthIndex(upperband=self.params.rsihigh, lowerband=self.params.rsilow)
        self.north = NorthValue(market=self.params.market)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

        if self.order:
            return

        if self.data.close[0] >= self.data.close[-self.params.smaperiod]:
            self.do_next(self.params.periodbull, self.params.highpercentbull, self.params.lowpercentbull,
                         self.params.maxdrawbackbull, 'bull')
        else:
            self.do_next(self.params.periodbear, self.params.highpercentbear, self.params.lowpercentbear,
                         self.params.maxdrawbackbear, 'bear')

    def do_next(self, period, highp, lowp, maxd, trend):
        today = self.datas[0].datetime.date()
        if period > 0:
            start_day = today - datetime.timedelta(days=period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]

        no_north_today = False
        if self.p.mode == 1:
            north_value_today = north_history.iloc[-1]['value']
        else:
            north_history_today = north_history.iloc[-1]['date_raw']
            if north_history_today == today.__str__():
                north_value_today = north_history.iloc[-1]['value']
            else:
                no_north_today = True
                north_value_today = 0

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * lowp)]['value']
        north_value_high = north_history.iloc[int(history_len * highp)]['value']

        has_position = True if self.getposition() else False

        rsi = self.rsi[0]

        next_log = '%s / Data %.3f / Today %.3f / Low %.3f / High %.5f / RSI %.3f / Trend %s' % (
            has_position, self.data.close[0], north_value_today, north_value_low, north_value_high, rsi, trend)
        self.last_next_log = next_log
        self.log(next_log)

        has_operation = False
        if has_position:
            if north_value_today < north_value_low or self.data.close[0] < self.buy_price * (1 - maxd):
                if no_north_today:
                    self.log('no north today sell')
                self.sell_stock(sell_reason=REASON_MAIN)
                has_operation = True
        else:
            if north_value_today > north_value_high:
                if no_north_today:
                    self.log('no north today buy')
                self.buy_stock(buy_reason=REASON_MAIN)
                has_operation = True

        if self.p.mode == 3:
            if not has_operation:
                if not has_position:
                    rsi1 = self.rsi[-1]
                    if rsi <= self.params.rsilow < rsi1:
                        self.buy_stock(buy_reason=REASON_SUPERLOW)
                else:
                    if self.buy_reason == REASON_SUPERLOW and self.in_market_days >= self.params.rsidays:
                        self.sell_stock(sell_reason=REASON_SUPERLOW)

        if self.p.mode == 4:
            if not has_operation:
                if not has_position:
                    rsi1 = self.rsi[-1]
                    if rsi <= self.params.rsilow < rsi1:
                        self.buy_stock(buy_reason=REASON_SUPERLOW)
                    elif rsi1 < self.params.rsihigh <= rsi:
                        self.buy_stock(buy_reason=REASON_SUPERHIGH)
                else:
                    if self.in_market_days >= self.params.rsidays:
                        if self.buy_reason == REASON_SUPERLOW:
                            self.sell_stock(sell_reason=REASON_SUPERLOW)
                        elif self.buy_reason == REASON_SUPERHIGH:
                            self.sell_stock(sell_reason=REASON_SUPERHIGH)
