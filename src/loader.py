import akshare as ak
import pandas as pd
import stocks


def get_datafile_name(stock_code):
    return "../data/daily/" + stock_code + "_data.csv"


def force_load_stock_history(stock_code):
    filename = get_datafile_name(stock_code)
    history = ak.stock_zh_index_daily(symbol=stock_code)
    history.to_csv(filename)
    return history


def load_stock_history(stock_code, start=None, end=None):
    filename = get_datafile_name(stock_code)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        history = force_load_stock_history(stock_code)
    return process_stock_history(history, start, end)


def process_stock_history(df, start=None, end=None):
    df[['date']] = df[['date']].apply(pd.to_datetime)
    df.set_index(keys=['date'], inplace=True)
    if start is None and end is None:
        return df
    elif start is None and end is not None:
        return df[:end]
    elif start is not None and end is None:
        return df[start:]
    else:
        return df.loc[start:end]


def force_load_north():
    force_load_north_single('all', '北上')
    force_load_north_single('sh', '沪股通')
    force_load_north_single('sz', '深股通')


def load_north_single(type, start=None, end=None):
    filename = get_datafile_name("north_%s" % type)
    try:
        history = pd.read_csv(filename)
    except FileNotFoundError:
        force_load_north()
        history = pd.read_csv(filename)
    return process_stock_history(history, start, end)


def force_load_north_single(type, indicator):
    filename = get_datafile_name("north_%s" % type)
    try:
        existing_history = pd.read_csv(filename)
    except FileNotFoundError:
        existing_history = None

    new_history = ak.stock_em_hsgt_north_net_flow_in(indicator=indicator)

    if existing_history is None:
        history = new_history
    else:
        history = existing_history.append(new_history).drop_duplicates(subset=['date', 'value'])
        history = history.drop(columns=['Unnamed: 0'])
        history.set_index(keys=[pd.Index(range(len(history)))], inplace=True)

    history.to_csv(filename)


if __name__ == '__main__':
    for stock in stocks.Stock:
        force_load_stock_history(stock.code)
        print('%s loaded' % stock.code)

    force_load_north()
    print('north loaded')
