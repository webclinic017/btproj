import backtrader as bt

import loader


class NorthValue(bt.Indicator):
    lines = (
        'north',
    )

    params = (
        ('market', 'sh'),
    )

    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

    def __init__(self):
        self.north_history = loader.load_north_single(self.params.market)

    def next(self):
        today = self.datas[0].datetime.date()
        north_history = self.north_history[:today]
        north_history_today = north_history.iloc[-1]['date_raw']
        if north_history_today == today.__str__():
            north_value_today = north_history.iloc[-1]['value']
        else:
            north_value_today = 0

        self.lines.north[0] = north_value_today
