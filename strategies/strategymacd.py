from backtrader.indicators import MACDHisto

from strategies.one_order_strategy import OneOrderStrategy


class StrategyMACD(OneOrderStrategy):
    params = (
        ('macd_period_me1', 12),
        ('macd_period_me2', 26),
        ('macd_period_signal', 9),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.macd_large = MACDHisto(self.data1,
                                    period_me1=self.p.macd_period_me1,
                                    period_me2=self.p.macd_period_me2,
                                    period_signal=self.p.macd_period_signal)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        if self.order:
            return

        has_position = True if self.getposition() else False
        macd_histo = self.macd_large.histo[0]
        # self.log('%s / MACD histo %.3f' % (has_position, macd_histo))

        if has_position:
            if macd_histo < 0:
                # if north_value_today < north_value_low:
                self.sell_stock()
        else:
            if macd_histo > 0:
                self.buy_stock()
