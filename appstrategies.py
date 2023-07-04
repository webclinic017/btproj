from stocks import Stock
from strategies.strategy4 import Strategy4
from strategies.strategy4phase import Strategy4Phase
from strategies.strategySMA import StrategySMA
from strategies.strategyaccu import StrategyAccuValue
from strategies.strategynorth import StrategyNorth
from strategies.strategynorthsma import StrategyNorthWithSMA


strategies = [
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 2 New Args",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5))"},
        "core": False
    },
    {
        "label": "Strategy4Phase for HS300ETF/CYB50ETF/ZZ500ETF mode 2",
        "class": Strategy4Phase,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5))", "buyperiod": 18, "sellperiod": 22, "minchgpct": 3, "shouldbuypct": 0, "halfrate": 50, "backdays": 3},
        "core": True
    },
    {
        "label": "Strategy4Phase for HS300ETF/CYB50ETF/ZZ500ETF/ZZ1000ETF mode 2",
        "class": Strategy4Phase,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.ZZ1000ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5), (24, 5))", "buyperiod": 19, "sellperiod": 19, "minchgpct": 2, "shouldbuypct": -0.7, "halfrate": 50, "backdays": 60},
        "core": False
    },
    {
        "label": "Strategy4Phase for HS300ETF/CYB50ETF/ZZ500ETF/KC50ETF mode 2 New Args",
        "class": Strategy4Phase,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.KC50ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5), (20, 5))", "buyperiod": 18, "sellperiod": 22, "minchgpct": 1, "shouldbuypct": -0.5, "halfrate": 10, "backdays": 3},
        "core": True
    },
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF/KC50ETF mode 2 New Args",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.KC50ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5), (20, 5))", "buyperiod": 16, "sellperiod": 19, "minchgpct": 3, "shouldbuypct": -1},
        "core": False
    },
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF/ZZ1000ETF mode 2 New Args",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF, Stock.ZZ1000ETF],
        "data_start": 30,
        "args": {"mode": 2, "buyperiod": 15, "sellperiod": 19, "minchgpct": 3, "shouldbuypct": -1, "rsi": "((30, 5), (25, 5), (24, 5), (24, 5))"},
        "core": False
    },
    {
        "label": "Strategy4 for HS300ETF/CYB50ETF/ZZ500ETF mode 2",
        "class": Strategy4,
        "stocks": [Stock.HS300ETF, Stock.CYB50ETF, Stock.ZZ500ETF],
        "data_start": 30,
        "args": {"mode": 2, "rsi": "((30, 5), (25, 5), (24, 5))", "buyperiod": 20, "sellperiod": 20, "minchgpct": 0, "shouldbuypct": 0.7},
        "core": False
    },
    {
        "label": "StrategyNorth for CYB50ETF",
        "class": StrategyNorth,
        "stocks": [Stock.CYB50ETF],
        "data_start": 0,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorth for A50ETF",
        "class": StrategyNorth,
        "stocks": [Stock.A50ETF],
        "data_start": 0,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorthWithSMA for CYB50ETF",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.CYB50ETF],
        "data_start": 60,
        "args": {},
        "core": True
    },
    {
        "label": "StrategyNorthWithSMA for A50ETF",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.A50ETF],
        "data_start": 60,
        "args": {},
        "core": False
    },
    {
        "label": "StrategyNorthWithSMA for A50ETF New Args",
        "class": StrategyNorthWithSMA,
        "stocks": [Stock.A50ETF],
        "data_start": 60,
        "args": {"periodbull": 250, "highpercentbull": 0.8, "lowpercentbull": 0.4, "maxdrawbackbull": 0.05,
                 "periodbear": 120, "highpercentbear": 0.9, "lowpercentbear": 0.2, "maxdrawbackbear": 0.1,
                 "smaperiod": 10, "modehalf": False},
        "core": True
    },
    {
        "label": "StrategySMA for CYB50ETF",
        "class": StrategySMA,
        "stocks": [Stock.CYB50ETF],
        "data_start": 60,
        "args": {"mode": 1},
        "core": False
    },
    {
        "label": "StrategyAccuValue for KZZETF",
        "class": StrategyAccuValue,
        "stocks": [Stock.KZZETF],
        "data_start": 0,
        "args": {"stock_code": Stock.KZZETF.code},
        "core": False
    }
]

for i in range(len(strategies)):
    strategies[i]["id"] = i


def get_strategies():
    return strategies