import pandas as pd
import requests
from akshare.stock_feature.stock_hist_em import code_id_map_em


def stock_zh_a_hist(
    code: str = "sh000001",
    period: str = "daily",
    start_date: str = "19700101",
    end_date: str = "20500101",
    adjust: str = "",
) -> pd.DataFrame:
    """
    东方财富网-行情首页-沪深京 A 股-每日行情
    http://quote.eastmoney.com/concept/sh603777.html?from=classic
    :param code: 股票代码
    :type symbol: str
    :param period: choice of {'daily', 'weekly', 'monthly'}
    :type period: str
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
    :type adjust: str
    :return: 每日行情
    :rtype: pandas.DataFrame
    """
    symbol = code[2:]
    code_id_dict = code_id_map_em()
    if symbol in code_id_dict and code != 'sh000001':
        code_id = code_id_dict[symbol]
    else:
        if code[0:2] == 'sh':
            code_id = 1
        else:
            code_id = 0
    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": period_dict[period],
        "fqt": adjust_dict[adjust],
        "secid": f"{code_id}.{symbol}",
        "beg": start_date,
        "end": end_date,
        "_": "1623766962675",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not (data_json["data"] and data_json["data"]["klines"]):
        return pd.DataFrame()
    temp_df = pd.DataFrame(
        [item.split(",") for item in data_json["data"]["klines"]]
    )
    temp_df.columns = [
        "date",
        "open",
        "close",
        "high",
        "low",
        "volume",           #成交量
        "volume_value",     #成交额
        "amplitude",        #振幅
        "volatility_ratio", #涨跌幅
        "volatility_price", #涨跌额
        "change_rate",      #换手率
    ]
    temp_df.index = pd.to_datetime(temp_df["date"])
    temp_df.reset_index(inplace=True, drop=True)

    temp_df["open"] = pd.to_numeric(temp_df["open"])
    temp_df["close"] = pd.to_numeric(temp_df["close"])
    temp_df["high"] = pd.to_numeric(temp_df["high"])
    temp_df["low"] = pd.to_numeric(temp_df["low"])
    temp_df["volume"] = pd.to_numeric(temp_df["volume"])
    temp_df["volume_value"] = pd.to_numeric(temp_df["volume_value"])
    temp_df["amplitude"] = pd.to_numeric(temp_df["amplitude"])
    temp_df["volatility_ratio"] = pd.to_numeric(temp_df["volatility_ratio"])
    temp_df["volatility_price"] = pd.to_numeric(temp_df["volatility_price"])
    temp_df["change_rate"] = pd.to_numeric(temp_df["change_rate"])

    return temp_df