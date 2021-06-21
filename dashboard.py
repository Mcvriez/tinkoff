#!/Users/vldq/PycharmProjects/tinkoff/venv/bin/python3

import yaml
from datetime import date, datetime, timedelta
from openapi_client import openapi
from pytz import timezone
from investpy import get_etf_recent_data, get_currency_cross_recent_data, get_bond_information, get_stocks_overview
from os import getcwd


cfg = yaml.load(open(f'/Users/vldq/PycharmProjects/tinkoff/config/t-config.yml'), Loader=yaml.BaseLoader)
figimap = yaml.load(open(f'/Users/vldq/PycharmProjects/tinkoff/config/figimap.yml'), Loader=yaml.BaseLoader)
TOKEN = cfg['token']
etfdict = cfg['etf_list']

year_to_date = date(date.today().year, 1, 1).isoformat()
today = datetime.now(tz=timezone('Europe/Moscow')).isoformat()

rub_usd_ratio = get_currency_cross_recent_data('USD/RUB').iloc[[-1]].Close.values[0]
eur_usd_ratio = get_currency_cross_recent_data('USD/EUR').iloc[[-1]].Close.values[0]
eur_rub_ratio = get_currency_cross_recent_data('EUR/RUB').iloc[[-1]].Close.values[0]


def operations(client):
    operations = client.operations.operations_get(year_to_date, today)
    operations = operations.payload.operations
    ops_map = dict.fromkeys(set([x.operation_type for x in operations]), 0)
    for o in operations:
        val = o.payment
        if o.currency == 'RUB':
            val /= rub_usd_ratio
        elif o.currency == 'EUR':
            val /= eur_usd_ratio
        ops_map[o.operation_type] += val
    ops_map = {k: round(v) for k, v in ops_map.items()}
    coup = ops_map["Coupon"] - ops_map["TaxCoupon"]
    div = ops_map["Dividend"] - ops_map["TaxDividend"]
    print(f'y2d rev:\t${coup + div}\t\tc:{int((coup / (div + coup)) * 100)}%')
    return operations, ops_map


def stats():
    total_usd = floating = etftotal = cash = 0

    # investing
    us_10_year = get_bond_information('U.S. 10Y').iloc[0]['Prev. Close']
    ru_10_year = get_bond_information('Russia 10Y').iloc[0]['Prev. Close']
    etf_prices = {x: get_etf_recent_data(x, 'united states').iloc[[-1]].Close.values[0]
                    for x in etfdict}

    # tinkoff
    client = openapi.api_client(TOKEN)
    positions = client.portfolio.portfolio_get().payload.positions
    on_hand = client.portfolio.portfolio_currencies_get().payload.currencies

    on_hand_str = '\t\t'.join([x.currency[:3] + str(round(x.balance)) for x in on_hand[::-1] if x.balance > 20])
    on_hand_str = on_hand_str.replace('USD', '$').replace('RUB', '₽').replace('EUR', '€')

    for pos in positions:
        exp = pos.balance * pos.average_position_price.value + pos.expected_yield.value
        fl = pos.expected_yield.value
        if pos.average_position_price.currency == 'RUB':
            exp /= rub_usd_ratio
            fl /= rub_usd_ratio
        elif pos.average_position_price.currency == 'EUR':
            exp /= eur_usd_ratio
            fl /= eur_usd_ratio
        total_usd += exp
        floating += fl
        if pos.instrument_type == 'Currency':
            cash += int(exp)
    cash += int([x.balance / rub_usd_ratio for x in on_hand if x.currency == 'RUB'].pop())

    for etf, price in etf_prices.items():
        total_usd += int(etfdict[etf]) * price
        etftotal += int(etfdict[etf]) * price

    year_ops, year_stats = operations(client)
    print(f'total:\t\t${round(total_usd / 1000, 1)}k\t\t€{round(total_usd / 1000 * eur_usd_ratio, 1)}k\n'
          f'floating:\t${round(floating / 1000, 1)}k\n'
          f'on hand:\t{on_hand_str}\n')  # ${cash}
    print('-' * 18)
    print(f'10 year us:\t{round(us_10_year, 2)}%\n'
          f'10 year ru:\t{ru_10_year}%\n')
    print(f'USD:\t\t{round(rub_usd_ratio, 1)}\n'
          f'EUR:\t\t{round(eur_rub_ratio, 1)}\n'
          f'ratio:\t\t{round(1 / eur_usd_ratio, 3)}\n')
    print('-' * 18)
    for o in year_ops:
        if o.date.date() >= (datetime.now() - timedelta(days=7)).date() \
                and o.operation_type in ['Coupon', 'Dividend', 'Repayment', 'PartRepayment']:
            print(o.currency, round(o.payment),  # o.date.date().strftime('%d'),
                  o.operation_type[:3], figimap.get(o.figi), sep='\t')


if __name__ == '__main__':
    stats()
