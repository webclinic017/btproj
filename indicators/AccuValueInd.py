import backtrader as bt

import loader


class AccuValueInd(bt.Indicator):
    lines = (
        'accu',
    )

    params = (
        ('stock_code', None),
    )

    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

    def __init__(self):
        self.accu_values = loader.load_etf_accu_history(self.params.stock_code)

    def next(self):
        today = self.datas[0].datetime.date()
        try:
            accu_today = self.accu_values.loc[str(today)]['accu_qfq'][0]
            self.lines.accu[0] = accu_today
        except:
            pass
