import backtrader as bt
from backtrader.indicators import MovingAverageSimple, RelativeStrengthIndex, MACD


class StrategyDisplay(bt.Strategy):

    def __init__(self):
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
        self.rsi = RelativeStrengthIndex()
        self.macd = MACD()
