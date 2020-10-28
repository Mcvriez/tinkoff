from openapi_client import openapi
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from lib import finviz


def get_positions(token):
    client = openapi.api_client(token)
    portfolio = client.portfolio.portfolio_get()
    df = pd.DataFrame.from_records([s.to_dict() for s in portfolio.payload.positions])
    df['currency'] = df['expected_yield'].apply(lambda x: x.get('currency'))
    df['floating'] = df['expected_yield'].apply(lambda x: x.get('value'))
    df['price'] = df['average_position_price'].apply(lambda x: x.get('value'))
    df['bond_orig_price'] = df[df['average_position_price_no_nkd'].notna()].apply(lambda x: x.get('value'))
    df['position'] = df['balance']
    df['type'] = df['instrument_type']
    df['ticker'] = df['ticker'].str.replace('.', '-')
    return df


def get_operations(token):
    _from = datetime.now(tz=timezone('Europe/Moscow')) - timedelta(days=10000)
    client = openapi.api_client(token)
    operations = client.operations.operations_get(_from.isoformat(),
                                                  datetime.now(tz=timezone('Europe/Moscow')).isoformat())
    ops = operations.payload.operations
    ops_df = pd.DataFrame([{'figi': x.figi,
                            'payment': x.payment, 'date': x.date,
                            'type': x.instrument_type,
                            'currency': x.currency,
                            'operation_type': x.operation_type}
                           for x in ops])
    ops = ops.loc[(ops['operation_type'] == 'Dividend') | (ops['operation_type'] == 'Coupon') | (ops['operation_type'] == 'TaxDividend') | (ops['operation_type'] == 'TaxCoupon')]
    ops['month'] = ops['date'].apply(lambda x: x.month)
    ops['date'] = ops['date'].apply(lambda x: x.date())
    return ops_df


def get_stock_info(token):
    df = get_positions(token)
    l = (sorted([x.replace('.', '-') for x in df['ticker'].tolist()]))
    stocks = finviz.get_stats(l)
    stocks.columns = stocks.columns.str.lower()
    stocks = stocks.rename(columns={'price': 'price_curr'})
    stocks['price_curr'] = stocks['price_curr'].astype(float)
    df = pd.merge(df, stocks, how='left', on=['ticker'])
    df['vol'] = (df['lots'] * df['price_curr']).round(0)
    df['change'] = (df['floating'] / df['vol'] * 100).round(2)
    df['change'] = df['change'].astype(str).apply(lambda x: x + '%')
    df = df.round({'change': 1})
    df = df.rename(columns={'price_x': 'price'})
    df = df.dropna(thresh=2)
    df['expected'] = (df['dividend'].str.replace('%', '').str.replace('-', '0').astype(float) * df['vol'] / 100)
    df = df.round(0)
    df['sector'] = df['sector'].str.replace('Communication Services', 'Networks')\
        .str.replace('Consumer Cyclical', 'Services')\
        .str.replace('Consumer Defensive', 'Foods')\
        .str.replace('Basic Materials', 'Materials')\
        .str.replace('Real Estate', 'REIT')
    return df


def current_ratio(dframe):
    dframe = dframe.loc[dframe['type'] == 'Currency']
    usd_ratio = float(dframe.loc[dframe['name'] == "Доллар США"]['average_position_price'].apply(lambda x: x.get('value')))
    return usd_ratio