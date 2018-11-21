import argparse
import sys
import ccxt
import json
import csv

def inputArgs():
    parser = argparse.ArgumentParser(description='Download Crypto Data')
    parser.add_argument('--exchange', default=None, help='exchange name (kraken, binance, etc.)')
    parser.add_argument('--apiKey', default=None, help='API key')
    parser.add_argument('--apiSecret', default=None, help='API secret')
    parser.add_argument("--start", default=None, help='start date (inclusive), example: 2018-10-19')
    parser.add_argument('--end', default=None, help='end date (exclusive), example: 2018-10-20')
    parser.add_argument('-v', action='store_true', default=False, help='verbose exchange logging')
    parser.add_argument('-l', action='store_true', default=False, help='log to file')
    args = parser.parse_args()

    if not args.exchange or not args.apiKey or not args.apiSecret or not args.start or not args.end:
        parser.print_help()
        sys.exit(1)
    return args

def makeExchange(name, apiKey, apiSecret, verbose=False):
    if name == "kraken":
        exchange = ccxt.kraken({
            'apiKey': apiKey,
            'secret': apiSecret,
            'verbose': verbose,
        })
    else:
        raise Exception("invalid exchange argument", name)
    return exchange

def main():
    symbol="XLM/USD"
    args = inputArgs()
    exchange = makeExchange(args.exchange, args.apiKey, args.apiSecret, args.v)
    filename = args.exchange + '_' + args.start + '_' + args.end + '_trades.csv'

    if not exchange.has['fetchTrades']:
        raise Exception("function missing")

    since = exchange.parse8601(args.start + 'T00:00:00.000Z')
    with open(filename, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # write header
        csv_writer.writerow(['currency_pair', 'ID', 'timestamp', 'side', 'price', 'amount', 'fee', 'cost'])

        # TODO paginate and write to file until we hit a date that is outside the range
        # TODO use fetch my trades here
        # TODO since param is not working here
        trades_json = exchange.fetch_trades(symbol=symbol, since=since, limit=200, params={})
        for trade in trades_json:
            csv_writer.writerow([trade['symbol'], trade['id'], trade['timestamp'], trade['side'], trade['price'], trade['amount'], trade['fee'], trade['cost']])

if __name__ == "__main__":
    main()
