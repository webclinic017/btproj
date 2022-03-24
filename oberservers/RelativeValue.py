from backtrader import Observer


class RelativeValue(Observer):
    alias = ('CashValue',)
    lines = ('value', )
    params = (
        ('starttradedt', None),
        ('data', None),
    )

    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

    first = True
    init_value = 0
    init_price = 0

    def next(self):
        if self.params.starttradedt is not None:
            if self.datas[0].datetime.date(0).__str__() < self.params.starttradedt:
                return

        if self.first:
            self.init_value = self._owner.broker.get_value()
            self.init_price = self.data[0]

        ratio = self._owner.broker.get_value() / self.init_value

        self.lines.value[0] = ratio * self.init_price

        self.first = False
