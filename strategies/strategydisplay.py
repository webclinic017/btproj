import backtrader as bt
from backtrader.indicators import MovingAverageSimple, RelativeStrengthIndex, MACD


class StrategyDisplay(bt.Strategy):

    params = (
        ('show_sma', True),
        ('show_rsi', True),
        ('show_macd', True)
    )

    def __init__(self):
        if self.p.show_sma:
            data_size = len(self.data0.array)
            if data_size > 5:
                self.sma5 = MovingAverageSimple(period=5)
            if data_size > 10:
                self.sma10 = MovingAverageSimple(period=10)
            if data_size > 20:
                self.sma20 = MovingAverageSimple(period=20)
            if data_size > 60:
                self.sma60 = MovingAverageSimple(period=60)
            if data_size > 120:
                self.sma120 = MovingAverageSimple(period=120)
        if self.p.show_rsi:
            self.rsi = RelativeStrengthIndex()
        if self.p.show_macd:
            self.macd = MACD()
