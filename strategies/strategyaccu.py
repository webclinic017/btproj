from indicators.AccuValueInd import AccuValueInd
from strategies.one_order_strategy import OneOrderStrategy


class StrategyAccuValue(OneOrderStrategy):
    params = (
        ('stock_code', None),
        ('buy_percent', -0.3),
        ('sell_percent', -0.5),
        ('starttradedt', None),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.accu = AccuValueInd(stock_code=self.p.stock_code)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

        if self.order:
            return

        has_position = True if self.getposition() else False
        close_today = self.data.close[0]
        accu_today = self.accu.accu[0]

        next_log = '%s / Close %.3f / Accu %.3f / (Accu - Close) %.3f' % (
            has_position, close_today, accu_today, accu_today - close_today)
        self.last_next_log = next_log
        self.log(next_log)

        if has_position and close_today > accu_today * (1 + self.p.buy_percent / 100):
            self.sell_stock()
        elif not has_position and close_today < accu_today * (1 + self.p.sell_percent / 100):
            self.buy_stock()
