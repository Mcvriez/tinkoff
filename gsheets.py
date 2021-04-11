import yaml
import pandas as pd
from lib import tinkoff
import gspread
from gspread_dataframe import set_with_dataframe


token = yaml.load(open('config/t-config.yaml'), Loader=yaml.BaseLoader)['token']


def main():
    gc = gspread.service_account(filename='config/g-key.json')
    stocks_sheet = gc.open("tinvest").sheet1
    rustock_sheet = gc.open("tinvest").worksheets()[1]
    bonds_sheet = gc.open("tinvest").worksheets()[2]
    ops_sheet = gc.open("tinvest").worksheets()[3]

    df = tinkoff.get_stock_info(token)
    ratio = tinkoff.current_ratio(df)

    stocks = df.loc[(df['sector'].notna()) & (df['currency'] != 'RUB')]
    stocks = stocks[['name', 'ticker', 'sector', 'lots',  'vol', 'floating', 'change',
                     "dividend", 'expected', "recom"]]
    stocks_sheet.clear()
    set_with_dataframe(stocks_sheet, stocks)

    bonds = df.loc[df['type'] == 'Bond']
    bonds = bonds[['type', 'ticker', 'name', 'currency', 'price', 'bond_orig_price', 'lots', 'floating']]
    bonds_sheet.clear()
    set_with_dataframe(bonds_sheet, bonds)

    rustocks = df.loc[(df['type'] == 'Stock') & (df['currency'] == 'RUB')]
    rustocks = rustocks[['type', 'ticker', 'name', 'currency', 'price', 'lots', 'floating']]
    rustock_sheet.clear()
    set_with_dataframe(rustock_sheet, rustocks)

    ops = tinkoff.get_operations(token)
    ops.loc[ops['currency'] == 'RUB', 'payment'] = (ops['payment'] / ratio).round(2)
    ops = pd.merge(ops, df, on='figi', how='left')
    ops = ops[['name', 'payment', 'date', 'month', 'operation_type']]
    ops_sheet.clear()
    set_with_dataframe(ops_sheet, ops)




main()
# print(get_positions().to_string())



