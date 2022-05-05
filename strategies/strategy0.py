from backtrader.indicators import RelativeStrengthIndex, Highest, Stochastic, Lowest

from strategies.one_order_strategy import OneOrderStrategy


class Strategy0(OneOrderStrategy):
    params = (
        ('starttradedt', None),
        ('period', 5),
        ('rsihigh', 80),
        ('rsilow', 25),
        ('printlog', True),
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.rsi = RelativeStrengthIndex(upperband=self.p.rsihigh, lowerband=self.p.rsilow)
        # self.rsi = Stochastic()
        self.highest = Highest(self.data.high, period=self.p.period-1)
        self.lowest = Lowest(self.data.low, period=self.p.period-1)

    def next(self):
        rsi = self.rsi[-self.p.period]
        rsi0 = self.rsi[-self.p.period-1]
        if rsi <= self.p.rsilow < rsi0 or rsi0 < self.p.rsihigh <= rsi:
            h = self.highest[0]
            l = self.lowest[0]
            cp = self.data.close[-self.p.period]
            op = self.data.open[-self.p.period+1]
            c0 = self.data.close[0]
            dt = str(self.data.datetime.date(-self.p.period))
            self.log('DT %s RSI %f OPENP %f HIGHP %f LOWP %f FINALP %f' % (dt, rsi, (op-cp)/cp*100, (h-cp)/cp*100, (l-cp)/cp*100, (c0-cp)/cp*100))
            self.log('DT %s HIGH %f LOW %f CP %f OP %f' % (dt, h, l, cp, op))
