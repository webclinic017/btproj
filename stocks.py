import enum

import backtrader as bt


class Stock(enum.Enum):
    HS300 = ('HS300', 'sh000300', '沪深300', True)
    ZZ500 = ('ZZ500', 'sh000905', '中证500', True)
    CYB50 = ('CYB50', 'sz399673', '创业板50', True)
    SZ50 = ('SZ50', 'sh000016', '上证50', True)
    CYB = ('CYB', 'sz399006', '创业板', True)
    KC50 = ('KC50', 'sh000688', '科创50', True)
    ZZ1000 = ('ZZ1000', 'sh000852', '中证1000', True)
    HS300ETF = ('HS300ETF', 'sh510310', '沪深300ETF', True)
    HS300ETF_2 = ('HS300ETF_2', 'sh510300', '沪深300ETF2', True)
    CYB50ETF = ('CYB50ETF', 'sz159949', '创业板50ETF', True)
    ZZ500ETF = ('ZZ500ETF', 'sh510500', '中证500ETF', True)
    A50ETF = ('A50ETF', 'sz159602', 'A50ETF', True)
    ZZ1000ETF = ('ZZ1000ETF', 'sh512100', '中证1000ETF', True)

    ZGHLWETF = ('ZGHLWETF', 'sh513050', '中概互联ETF')
    ZQETF = ('ZQETF', 'sh512880', '证券ETF')
    QSETF = ('QSETF', 'sh512000', '券商ETF')
    HJETF = ('HJETF', 'sh518880', '黄金ETF')
    JETF = ('JETF', 'sh512690', '酒ETF')
    XNYCETF = ('XNYCETF', 'sh515030', '新能源车ETF')
    NZETF = ('NZETF', 'sh513100', '纳斯达克100ETF')
    YHETF = ('YHETF', 'sh512800', '银行ETF')
    XPETF = ('XPETF', 'sz159995', '芯片ETF')
    BDTETF = ('BDTETF', 'sh512480', '半导体ETF')
    YYETF = ('YYETF', 'sh512010', '医药ETF')
    KZZETF = ('KZZETF', 'sh511380', '可转债ETF')
    JGETF = ('JGETF', 'sh512660', '军工ETF')

    def __init__(self, stockname: str, code: str, cnname: str, core: bool = False):
        self.stockname = stockname
        self.code = code
        self.cnname = cnname
        self.core = core;


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