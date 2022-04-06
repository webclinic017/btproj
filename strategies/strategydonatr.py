from backtrader.indicators import AverageTrueRange, MovingAverageSimple

from indicators.DonChainChannels import DonChainChannels
from strategies.one_order_strategy import OneOrderStrategy


class StrategyDonAtr(OneOrderStrategy):
    params = (
        ('period', 20),
        ('stoplossatr', 1),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.count = 0

        self.sma = MovingAverageSimple(period=self.params.period*5)
        self.don = DonChainChannels(period=self.params.period)
        self.atr = AverageTrueRange(period=7)

    def next(self):
        OneOrderStrategy.next(self)

        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        if self.order:
            return

        if self.getposition():
            upper = self.don.upper[0]
            if self.in_market_days <= self.params.period:
                upper = max(self.data.close.get(size=self.in_market_days))
            if self.data.close[0] < upper - self.params.stoplossatr * self.atr.atr[0]:
            # if self.don.lower[0] < self.don.lower[-1]:# - self.params.stoplossatr * self.atr.atr[0]:
            # if self.don.upper[0] < self.don.upper[-1]:
                self.sell_stock()
        else:
            # if self.don.upper[0] > self.don.upper[-1] and self.don.middle[0] > self.sma[0]:# + self.params.stoplossatr * self.atr.atr[0]:
            if self.don.lower[0] > self.don.lower[-1] and self.data.close[0] > self.sma[0] and self.sma[0] >= self.sma[-1]:
                self.buy_stock()