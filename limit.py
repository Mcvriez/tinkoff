from openapi_client import openapi
from dashboard import TOKEN

client = openapi.api_client(TOKEN)
figi = client.market.market_search_by_ticker_get('MRK').payload.instruments[0].figi

request = {
  "lots": 1,
  "operation": "Buy",
  "price": 55
}
order = client.orders.orders_limit_order_post(figi, request)
print(order)


'''Send output to stdout. The primary output for your command should go to stdout. Anything that is machine readable should also go to stdout—this is where piping sends things by default.

Send messaging to stderr. Log messages, errors, and so on should all be sent to stderr. This means that when commands are piped together, these messages are displayed to the user and not fed into the next command.

Display help text when passed no options, the -h flag, or the --help flag.

Display a concise help text by default. If you can, display help by default when myapp or myapp subcommand is run. Unless your program is very simple and does something obvious by default (e.g. ls), or your program reads input interactively (e.g. cat).
'''

