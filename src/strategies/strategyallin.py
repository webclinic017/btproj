from strategies.one_order_strategy import OneOrderStrategy


class StrategyAllIn(OneOrderStrategy):
    params = (
        ('period', 500),
        ('printlog', True)
    )

    def __init__(self):
        OneOrderStrategy.__init__(self)

    def next(self):
        if self.order:
            return

        has_position = True if self.getposition() else False
        if has_position:
            pass
        else:
            self.buy_stock()
