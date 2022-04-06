import backtrader as bt


class DonChainChannels(bt.Indicator):
    lines = (
        'upper',
        'middle',
        'lower',
    )

    params = (
        ('period', 20),
    )

    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

    def next(self):
        # highs = self.data.high.get(size=self.p.period)
        # lows = self.data.low.get(size=self.p.period)
        highs = self.data.close.get(size=self.p.period)
        lows = self.data.close.get(size=self.p.period)
        if len(highs) > 0 and len(lows) > 0:
            upper = max(highs)
            lower = min(lows)
            self.lines.upper[0] = upper
            self.lines.lower[0] = lower
            self.lines.middle[0] = (upper + lower) / 2
