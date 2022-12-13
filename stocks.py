import enum

import backtrader as bt


class Stock(enum.Enum):
    HS300 = ('HS300', 'sh000300', '沪深300', False, True)
    ZZ500 = ('ZZ500', 'sh000905', '中证500', False, True)
    CYB50 = ('CYB50', 'sz399673', '创业板50', False, True)
    SZ50 = ('SZ50', 'sh000016', '上证50', False, True)
    CYB = ('CYB', 'sz399006', '创业板', False, True)
    KC50 = ('KC50', 'sh000688', '科创50', False, True)
    ZZ1000 = ('ZZ1000', 'sh000852', '中证1000', False, True)
    GZ2000 = ('GZ2000', 'sz399303', '国证2000', False, True)

    HS300ETF = ('HS300ETF', 'sh510310', '沪深300ETF', True, False)
    HS300ETF_2 = ('HS300ETF_2', 'sh510300', '沪深300ETF2', True, False)
    CYB50ETF = ('CYB50ETF', 'sz159949', '创业板50ETF', True, False)
    ZZ500ETF = ('ZZ500ETF', 'sh510500', '中证500ETF', True, False)
    A50ETF = ('A50ETF', 'sz159602', 'A50ETF', True, False)
    ZZ1000ETF = ('ZZ1000ETF', 'sh512100', '中证1000ETF', True, False)
    KC50ETF = ('KC50ETF', 'sh588000', '科创50ETF', True, False)
    GZ2000ETF = ('GZ2000ETF', 'sz159628', '国证2000ETF', True, False)

    ZGHLWETF = ('ZGHLWETF', 'sh513050', '中概互联ETF', False, False)
    ZQETF = ('ZQETF', 'sh512880', '证券ETF', False, False)
    QSETF = ('QSETF', 'sh512000', '券商ETF', False, False)
    HJETF = ('HJETF', 'sh518880', '黄金ETF', False, False)
    JETF = ('JETF', 'sh512690', '酒ETF', False, False)
    XNYCETF = ('XNYCETF', 'sh515030', '新能源车ETF', False, False)
    NZETF = ('NZETF', 'sh513100', '纳斯达克100ETF', False, False)
    YHETF = ('YHETF', 'sh512800', '银行ETF', False, False)
    XPETF = ('XPETF', 'sz159995', '芯片ETF', False, False)
    BDTETF = ('BDTETF', 'sh512480', '半导体ETF', False, False)
    YYETF = ('YYETF', 'sh512010', '医药ETF', False, False)
    KZZETF = ('KZZETF', 'sh511380', '可转债ETF', False, False)
    JGETF = ('JGETF', 'sh512660', '军工ETF', False, False)

    def __init__(self, stockname: str, code: str, cnname: str, core: bool = False, is_index: bool = False):
        self.stockname = stockname
        self.code = code
        self.cnname = cnname
        self.core = core
        self.is_index = is_index


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