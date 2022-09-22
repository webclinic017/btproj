import backtrader as bt

import loader


class AccuValue(bt.Observer):
    lines = (
        'accu',
    )

    params = (
        ('stock_code', None),
        ('start_date', '20000101'),
    )

    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

    def __init__(self):
        self.accu_values = loader.load_etf_accu_history(self.params.stock_code, start=self.params.start_date)

    def next(self):
        today = self.datas[0].datetime.date()
        try:
            accu_today = self.accu_values.loc[str(today)]['accu_qfq'][0]
            self.lines.accu[0] = accu_today
        except:
            pass
