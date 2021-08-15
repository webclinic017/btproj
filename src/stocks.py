import backtrader as bt
import enum

from loader import load_stock_history
from typing import List


class Stock(enum.Enum):
    HS300 = ('HS300', 'sh000300')
    ZZ500 = ('ZZ500', 'sh000905')
    CYB50 = ('CYB50', 'sz399673')
    SZ50 = ('SZ50', 'sh000016')
    CYB = ('CYB', 'sz399006')
    KC50 = ('KC50', 'sh000688')
    HS300ETF = ('HS300ETF', 'sh510310')
    CYB50ETF = ('CYB50ETF', 'sz159949')

    def __init__(self, stockname: str, code: str):
        self.stockname = stockname
        self.code = code


class StockData:

    def __init__(self, stock: Stock, data: bt.feeds.feed.DataBase):
        self.stock = stock
        self.data = data


def load_stock_data(cerebro: bt.Cerebro, stocks: List[Stock], start: str, end: str):
    for stock in stocks:
        df = load_stock_history(stock.code, start, end)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name=stock.stockname)
