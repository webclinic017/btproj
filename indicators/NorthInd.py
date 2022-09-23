import datetime
import backtrader as bt
import loader


class NorthValue(bt.Indicator):
    lines = (
        'north',
        'high',
        'low',
    )

    params = (
        ('market', 'sh'),
        ('periodbull', 500),
        ('highpercentbull', 0.8),
        ('lowpercentbull', 0.2),
        ('periodbear', 60),
        ('highpercentbear', 0.9),
        ('lowpercentbear', 0.4),
        ('smaperiod', 20)
    )

    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

    def __init__(self):
        self.north_history = loader.load_north_single(self.params.market)

    def next(self):
        if self.data.close[0] >= self.data.close[-self.p.smaperiod]:
            (north_value_today, north_value_high, north_value_low) \
                = self.calculate(self.p.periodbull, self.p.highpercentbull, self.p.lowpercentbull)
        else:
            (north_value_today, north_value_high, north_value_low) \
                = self.calculate(self.p.periodbear, self.p.highpercentbear, self.p.lowpercentbear)

        self.lines.north[0] = north_value_today
        self.lines.high[0] = north_value_high
        self.lines.low[0] = north_value_low

    def calculate(self, period, highp, lowp):
        today = self.datas[0].datetime.date()
        if period > 0:
            start_day = today - datetime.timedelta(days=period)
            north_history = self.north_history[start_day:today]
        else:
            north_history = self.north_history[:today]
        north_history_today = north_history.iloc[-1]['date_raw']
        if north_history_today == today.__str__():
            north_value_today = north_history.iloc[-1]['value']
        else:
            north_value_today = 0

        north_history.sort_values(by=['value'], inplace=True)
        history_len = len(north_history)
        north_value_low = north_history.iloc[int(history_len * lowp)]['value']
        north_value_high = north_history.iloc[int(history_len * highp)]['value']

        return north_value_today, north_value_high, north_value_low
