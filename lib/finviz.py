from finviz.screener import Screener
import pandas as pd

# fz = "https://finviz.com/screener.ashx?v=152&ft=4&o=-dividendyield&c=0,1,2,3,4,5,6,7,10,11,14,19,30,31,38,39,40,62,65,66,67,68"
custom = [str(x) for x in [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 14, 19, 30, 38, 62, 65]]


def get_stats(tickers=None):
    stock_list1 = Screener(tickers[:60], custom=custom)
    stock_list2 = Screener(tickers[60:], custom=custom)
    df1 = pd.DataFrame.from_records(stock_list1)
    df2 = pd.DataFrame.from_records(stock_list2)
    frames = [df1, df2]
    df = pd.concat(frames, sort=True)

    return df
