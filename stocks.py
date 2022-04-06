import enum

import backtrader as bt


class Stock(enum.Enum):
    HS300 = ('HS300', 'sh000300')
    ZZ500 = ('ZZ500', 'sh000905')
    CYB50 = ('CYB50', 'sz399673')
    SZ50 = ('SZ50', 'sh000016')
    CYB = ('CYB', 'sz399006')
    KC50 = ('KC50', 'sh000688')
    HS300ETF = ('HS300ETF', 'sh510310')
    HS300ETF_2 = ('HS300ETF_2', 'sh510300')
    CYB50ETF = ('CYB50ETF', 'sz159949')
    ZZ500ETF = ('ZZ500ETF', 'sh510500')
    A50ETF = ('A50ETF', 'sz159602')

    ZGHLWETF = ('ZGHLWETF', 'sh513050')
    ZQETF = ('ZQETF', 'sh512880')
    QSETF = ('QSETF', 'sh512000')
    HJETF = ('HJETF', 'sh518880')
    JETF = ('JETF', 'sh512690')
    XNYCETF = ('XNYCETF', 'sh515030')
    NZETF = ('NZETF', 'sh513100')
    YHETF = ('YHETF', 'sh512800')
    XPETF = ('XPETF', 'sz159995')
    BDTETF = ('BDTETF', 'sh512480')
    YYETF = ('YYETF', 'sh512010')
    KZZETF = ('KZZETF', 'sh511380')
    JGETF = ('JGETF', 'sh512660')




    def __init__(self, stockname: str, code: str):
        self.stockname = stockname
        self.code = code


class StockData:

    def __init__(self, stock: Stock, data: bt.feeds.feed.DataBase):
        self.stock = stock
        self.data = data


class PEMarket(enum.Enum):
    SH_A = ('SH_A', 'sh')
    SZ_A = ('SZ_A', 'sz')
    ZX = ('ZX', 'zx')
    CY = ('CY', 'cy')
    # KC = ('KC', 'kc')
    ALL = ('All', 'all')
    HS300 = ('HS300', '000300.XSHG')
    SZ50 = ('SZ50', '000016.XSHG')
    ZZ500 = ('ZZ500', '000905.XSHG')

    def __init__(self, market: str, code: str):
        self.market = market
        self.code = code