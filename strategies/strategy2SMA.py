from backtrader.indicators import MovingAverageSimple, Highest, AverageTrueRange

from strategies.one_order_strategy import OneOrderStrategy


class Strategy2SMA(OneOrderStrategy):

    params = (
        ('smaperiodfast', 10),
        ('smaperiodslow1', 20),
        ('smaperiodslow2', 30),
        ('starttradedt', None),
        ('mode', 1),
        ('atrratio', 1),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)
        self.smafast = MovingAverageSimple(period=self.params.smaperiodfast)
        self.smaslow1 = MovingAverageSimple(period=self.params.smaperiodslow1)
        self.smaslow2 = MovingAverageSimple(period=self.params.smaperiodslow2)
        self.atrfast = AverageTrueRange(period=self.params.smaperiodfast)
        self.atrslow1 = AverageTrueRange(period=self.params.smaperiodslow1)
        self.atrslow2 = AverageTrueRange(period=self.params.smaperiodslow2)

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        self.check_first_day()

        OneOrderStrategy.next(self)

        if self.order:
            return

        has_position = True if self.getposition() else False

        smafast_today = self.smafast[0]
        smaslow1_today = self.smaslow1[0]
        smaslow2_today = self.smaslow2[0]


        next_log = '%s / Data %.3f / Fast %.3f / Slow1 %.3f / Slow2 %.3f' \
                   % (has_position, self.data.close[0], smafast_today, smaslow1_today, smaslow2_today)
        self.last_next_log = next_log
        self.log(next_log)

        if has_position:
            if smafast_today < smaslow1_today:
                self.sell_stock()
        else:
            if self.p.mode == 1:
                if smafast_today > smaslow2_today:
                    self.buy_stock()
            elif self.p.mode == 2:
                if smafast_today > smaslow2_today and self.data.close[0] - self.data.close[-1] > self.atrfast[0]:
                    self.buy_stock()
            elif self.p.mode == 3:
                if smafast_today > smaslow2_today and self.data.close[0] - self.smafast[0] > self.atrfast[0] * self.p.atrratio:
                    self.buy_stock()
