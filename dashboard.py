from investpy import get_etf_recent_data, get_currency_cross_recent_data, get_bond_information,get_bonds_dict
import yaml
from openapi_client import openapi

cfg = yaml.load(open('config/t-config.yaml'), Loader=yaml.BaseLoader)
TOKEN = cfg['token']
etfdict = cfg['etf_list']


def main():
    total_usd = floating = etftotal = cash = 0

    # investing
    etf_prices = {x: get_etf_recent_data(x, 'united states').iloc[[-1]].Close.values[0]
                    for x in etfdict}
    rub_usd_ratio = get_currency_cross_recent_data('USD/RUB').iloc[[-1]].Close.values[0]
    eur_usd_ratio = get_currency_cross_recent_data('USD/EUR').iloc[[-1]].Close.values[0]
    eur_rub_ratio = get_currency_cross_recent_data('EUR/RUB').iloc[[-1]].Close.values[0]
    us_10_year = get_bond_information('U.S. 10Y').iloc[0]['Prev. Close']
    ru_10_year = get_bond_information('Russia 10Y').iloc[0]['Prev. Close']

    # tinkoff
    client = openapi.api_client(TOKEN)
    positions = client.portfolio.portfolio_get().payload.positions

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
            cash += exp + fl

    for etf, price in etf_prices.items():
        total_usd += int(etfdict[etf]) * price
        etftotal += int(etfdict[etf]) * price

    usd_stocks = [x for x in positions
                  if x.average_position_price.currency == 'USD'
                  and x.instrument_type == 'Stock']

    rub_stocks = [x for x in positions
                  if x.average_position_price.currency == 'RUB'
                  and x.instrument_type == 'Stock']

    eur_stocks = [x for x in positions
                  if x.average_position_price.currency == 'EUR'
                  and x.instrument_type == 'Stock']

    usd_bonds = [x for x in positions
                  if x.average_position_price.currency == 'USD'
                  and x.instrument_type == 'Bond']

    rub_bonds = [x for x in positions
                  if x.average_position_price.currency == 'RUB'
                  and x.instrument_type == 'Bond']

    print(f'exposure:\t{round(total_usd - floating)}\n'
          f'cash:\t\t{round(cash)}\n'
          f'floating:\t{round(floating)}\n\n'
          f'total:\t\t{round(total_usd)}')
    print('-' * 20)
    print(f'USD:\t\t{round(rub_usd_ratio, 2)}\n'
          f'EUR:\t\t{round(eur_rub_ratio, 2)}\n'
          f'ratio:\t\t{round(eur_usd_ratio, 3)}')
    print('-' * 20)
    print(f'10 year US:\t{round(us_10_year, 2)}%\n'
          f'10 year RU:\t{ru_10_year}%')


# main()
print(get_bonds_dict())
